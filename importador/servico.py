"""Servico de importacao: orquestra planilha -> deteccao de tipo -> banco."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Union

from . import banco
from .config import ConfiguracaoConexao
from .planilha import ler_planilha
from .tipos import analisar_colunas, converter_dataframe

Logger = Callable[[str], None]


class ModoImportacao(str, Enum):
    SUBSTITUIR = "substituir"  # esvazia a tabela antes de carregar a planilha
    ADICIONAR = "adicionar"  # mantem o que ja existe e so acrescenta linhas


@dataclass(frozen=True)
class ResultadoImportacao:
    linhas_lidas: int
    linhas_na_tabela: int

    @property
    def contagem_bate(self) -> bool:
        return self.linhas_lidas <= self.linhas_na_tabela


def importar(
    config: ConfiguracaoConexao,
    caminho_planilha: Union[str, Path],
    tabela: str,
    modo: ModoImportacao,
    log: Logger = print,
) -> ResultadoImportacao:
    engine = banco.criar_engine(config)
    repositorio = banco.TabelaRepository(engine, tabela)

    log(f"Lendo planilha: {caminho_planilha}")
    df = ler_planilha(caminho_planilha)
    log(f"{len(df)} linhas e {len(df.columns)} colunas encontradas na planilha.")

    log("Analisando o tipo de cada coluna (numero, data ou texto)...")
    tipos = analisar_colunas(df, log=log)

    tabela_foi_truncada = False
    if modo is ModoImportacao.SUBSTITUIR:
        tabela_foi_truncada = repositorio.truncar()
        if tabela_foi_truncada:
            log(f"Tabela '{tabela}' esvaziada antes de receber os dados novos.")

    repositorio.garantir_colunas(tipos, corrigir_tipo_existente=tabela_foi_truncada, log=log)

    log("Convertendo os valores da planilha para os tipos corretos...")
    df = converter_dataframe(df, tipos)

    log("Enviando os dados para o banco (pode demorar em planilhas grandes)...")
    df.to_sql(tabela, engine, if_exists="append", index=False, chunksize=2000, method=None)

    total = repositorio.contar_linhas()

    log("Criando índices nas colunas de id (acelera consultas e junções)...")
    repositorio.criar_indices_automaticos(df, log=log)

    # "Importacao concluida" fica por ultimo de proposito - e' o aviso final
    # pro usuario, mesmo que o processo em si (indices) ja tenha rodado antes.
    log(f"Importacao concluida. A tabela '{tabela}' agora tem {total} linhas no total.")

    resultado = ResultadoImportacao(linhas_lidas=len(df), linhas_na_tabela=total)
    if modo is ModoImportacao.SUBSTITUIR and total != len(df):
        log(
            f"ATENCAO: a planilha tinha {len(df)} linhas mas a tabela ficou com {total}. "
            "Confira antes de considerar concluido."
        )
    return resultado
