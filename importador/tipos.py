"""Deteccao do tipo de dado real de cada coluna de uma planilha.

Regra geral: so classifica uma coluna como numero ou data quando TODOS os
valores confirmam isso sem nenhuma ambiguidade (sem zero a esquerda perdido,
sem estourar o tamanho do tipo, sem formato de data inconsistente). Qualquer
duvida real, a coluna fica como texto. Isso preserva o valor exatamente como
veio da planilha.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Callable, Optional, Union

import pandas as pd

ValorConvertido = Union[str, int, Decimal, date, datetime, None]

_PADRAO_INTEIRO = re.compile(r"^-?\d+$")
_PADRAO_DECIMAL = re.compile(r"^-?\d+\.\d+$")

# Numeros com mais digitos que isso antes da virgula normalmente sao
# identificadores/codigos (ex: chave de NF-e com 44 digitos), nao quantidades.
_MAXIMO_DIGITOS_INTEIROS = 18

# Cada formato e' testado contra a coluna inteira; so vale se TODOS os valores baterem.
_FORMATOS_DATA: list[tuple[str, bool]] = [
    ("%Y-%m-%d %H:%M:%S.%f", True),
    ("%Y-%m-%d %H:%M:%S", True),
    ("%d/%m/%Y %H:%M:%S", True),
    ("%Y-%m-%d", False),
    ("%d/%m/%Y", False),
]


class TipoColuna(str, Enum):
    INTEIRO = "inteiro"
    DECIMAL = "decimal"
    DATA = "data"
    DATA_HORA = "data_hora"
    TEXTO = "texto"


@dataclass(frozen=True)
class InfoTipo:
    """Detalhes extras necessarios pra montar o tipo SQL (precisao, formato)."""

    precisao: Optional[int] = None
    escala: Optional[int] = None
    formato: Optional[str] = None


_FAMILIAS_SQL: dict[TipoColuna, set[str]] = {
    TipoColuna.TEXTO: {"text", "varchar", "longtext", "mediumtext", "tinytext", "char"},
    TipoColuna.INTEIRO: {"int", "bigint", "smallint", "tinyint", "mediumint"},
    TipoColuna.DECIMAL: {"decimal", "numeric", "double", "float"},
    TipoColuna.DATA: {"date"},
    TipoColuna.DATA_HORA: {"datetime", "timestamp"},
}


_DetectorTipo = Callable[[pd.Series], Optional[tuple[TipoColuna, InfoTipo]]]


def _detectar_inteiro(valores: pd.Series) -> Optional[tuple[TipoColuna, InfoTipo]]:
    info = _tentar_inteiro(valores)
    return (TipoColuna.INTEIRO, info) if info is not None else None


def _detectar_decimal(valores: pd.Series) -> Optional[tuple[TipoColuna, InfoTipo]]:
    info = _tentar_decimal(valores)
    return (TipoColuna.DECIMAL, info) if info is not None else None


def _detectar_data(valores: pd.Series) -> Optional[tuple[TipoColuna, InfoTipo]]:
    return _tentar_data(valores)


# Estrategias de deteccao, testadas nessa ordem ate uma delas confirmar o tipo.
# A ordem importa: um inteiro tambem bateria com o padrao de decimal, entao
# inteiro precisa vir primeiro; data so entra por ultimo por ser a checagem
# mais especifica (formato exato).
_DETECTORES: tuple[_DetectorTipo, ...] = (_detectar_inteiro, _detectar_decimal, _detectar_data)


def inferir_tipo_coluna(serie: pd.Series) -> tuple[TipoColuna, InfoTipo]:
    """Analisa uma coluna (Series de strings/None) e decide o tipo mais especifico
    que representa todos os valores sem risco de alteracao."""
    valores = serie.dropna().astype(str)
    valores = valores[valores.str.len() > 0]
    if valores.empty:
        return TipoColuna.TEXTO, InfoTipo()

    for detectar in _DETECTORES:
        resultado = detectar(valores)
        if resultado is not None:
            return resultado

    return TipoColuna.TEXTO, InfoTipo()


def _tem_zero_a_esquerda(valores_sem_sinal: pd.Series) -> bool:
    return bool(((valores_sem_sinal.str.len() > 1) & valores_sem_sinal.str.startswith("0")).any())


def _tentar_inteiro(valores: pd.Series) -> Optional[InfoTipo]:
    if not valores.str.match(_PADRAO_INTEIRO).all():
        return None
    corpo = valores.str.lstrip("-")
    if _tem_zero_a_esquerda(corpo):
        return None
    if int(corpo.str.len().max()) > _MAXIMO_DIGITOS_INTEIROS:
        return None
    return InfoTipo()


def _tentar_decimal(valores: pd.Series) -> Optional[InfoTipo]:
    eh_decimal_ou_inteiro = valores.str.match(_PADRAO_DECIMAL) | valores.str.match(_PADRAO_INTEIRO)
    if not eh_decimal_ou_inteiro.all():
        return None

    corpo = valores.str.lstrip("-")
    partes = corpo.str.split(".", n=1, expand=True)
    parte_inteira = partes[0]
    parte_decimal = partes[1].fillna("") if 1 in partes else pd.Series([""] * len(partes))

    if _tem_zero_a_esquerda(parte_inteira):
        return None

    max_inteiros = int(parte_inteira.str.len().max())
    max_decimais = int(parte_decimal.str.len().max())
    precisao = max_inteiros + max_decimais

    if max_inteiros > _MAXIMO_DIGITOS_INTEIROS:
        return None  # numero grande demais pra ser uma quantidade real (provavelmente um codigo)
    if not (0 < precisao <= 65):  # 65 e' o limite de precisao do DECIMAL no MySQL/MariaDB
        return None

    return InfoTipo(precisao=precisao, escala=max_decimais)


def _tentar_data(valores: pd.Series) -> Optional[tuple[TipoColuna, InfoTipo]]:
    for formato, tem_hora in _FORMATOS_DATA:
        try:
            pd.to_datetime(valores, format=formato, errors="raise")
        except (ValueError, TypeError):
            continue
        tipo = TipoColuna.DATA_HORA if tem_hora else TipoColuna.DATA
        return tipo, InfoTipo(formato=formato)
    return None


def tipo_sql(tipo: TipoColuna, info: InfoTipo) -> str:
    """Traduz o tipo detectado pro tipo de coluna equivalente no MySQL/MariaDB."""
    if tipo is TipoColuna.INTEIRO:
        return "bigint"
    if tipo is TipoColuna.DECIMAL:
        return f"decimal({info.precisao},{info.escala})"
    if tipo is TipoColuna.DATA:
        return "date"
    if tipo is TipoColuna.DATA_HORA:
        return "datetime"
    return "text"


def familia_sql(tipo_sql_atual: str) -> TipoColuna:
    """A qual TipoColuna um tipo SQL existente no banco pertence (pra comparar
    com o tipo recem-detectado e decidir se precisa alterar a coluna)."""
    base = str(tipo_sql_atual).split("(")[0].strip().lower()
    for familia, nomes in _FAMILIAS_SQL.items():
        if base in nomes:
            return familia
    return TipoColuna.TEXTO


def converter_valor(valor: object, tipo: TipoColuna, info: InfoTipo) -> ValorConvertido:
    """Converte um valor (string ou None) lido da planilha pro tipo Python
    equivalente ao tipo de coluna detectado."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    if tipo is TipoColuna.INTEIRO:
        return int(valor)
    if tipo is TipoColuna.DECIMAL:
        return Decimal(valor)
    if tipo is TipoColuna.DATA:
        return datetime.strptime(valor, info.formato).date()
    if tipo is TipoColuna.DATA_HORA:
        return datetime.strptime(valor, info.formato)
    return valor


def analisar_colunas(
    df: pd.DataFrame, log=print
) -> dict[str, tuple[TipoColuna, InfoTipo]]:
    """Roda a deteccao de tipo em cada coluna do dataframe e loga o resultado."""
    tipos: dict[str, tuple[TipoColuna, InfoTipo]] = {}
    for coluna in df.columns:
        tipo, info = inferir_tipo_coluna(df[coluna])
        tipos[coluna] = (tipo, info)
        log(f"  - {coluna}: {tipo_sql(tipo, info)}")
    return tipos


def converter_dataframe(
    df: pd.DataFrame, tipos: dict[str, tuple[TipoColuna, InfoTipo]]
) -> pd.DataFrame:
    for coluna, (tipo, info) in tipos.items():
        if tipo is not TipoColuna.TEXTO:
            df[coluna] = df[coluna].apply(lambda v: converter_valor(v, tipo, info))
    return df
