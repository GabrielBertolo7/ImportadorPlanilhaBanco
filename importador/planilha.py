"""Leitura de planilhas (xlsx/xls/csv) e normalizacao de nomes de coluna."""
from __future__ import annotations

import unicodedata
from pathlib import Path
from typing import Iterable, Union

import pandas as pd


def normalizar_nome_coluna(nome: object) -> str:
    """Vira um nome de coluna SQL valido: minusculo, sem acento/espaco/simbolo."""
    texto = str(nome).strip().lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = "".join(ch if ch.isalnum() else "_" for ch in texto)
    while "__" in texto:
        texto = texto.replace("__", "_")
    texto = texto.strip("_")
    if not texto:
        texto = "coluna"
    if texto[0].isdigit():
        texto = f"c_{texto}"
    return texto


def resolver_nomes_duplicados(colunas: Iterable[object]) -> list[str]:
    """Se a planilha tiver duas colunas com o mesmo nome (ex: duas 'id'), numera
    a partir da segunda ocorrencia, pra nao colidir no banco."""
    vistos: dict[str, int] = {}
    novas = []
    for coluna in colunas:
        base = normalizar_nome_coluna(coluna)
        if base in vistos:
            vistos[base] += 1
            novas.append(f"{base}_{vistos[base]}")
        else:
            vistos[base] = 1
            novas.append(base)
    return novas


def ler_planilha(caminho_arquivo: Union[str, Path]) -> pd.DataFrame:
    """Le a planilha inteira como texto puro (sem interpretar numero/data ainda);
    a deteccao de tipo acontece depois, em importador.tipos."""
    caminho_arquivo = str(caminho_arquivo)
    if caminho_arquivo.lower().endswith(".csv"):
        df = pd.read_csv(caminho_arquivo, dtype=str)
    else:
        df = pd.read_excel(caminho_arquivo, dtype=str)
    df = df.astype(object).where(df.notna(), None)
    df.columns = resolver_nomes_duplicados(df.columns)
    return df
