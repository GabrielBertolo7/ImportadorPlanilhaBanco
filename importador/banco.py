"""Conexao e operacoes de estrutura (DDL) no banco de dados MySQL/MariaDB."""
from __future__ import annotations

import re
from datetime import datetime
from typing import Callable

import pandas as pd
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from .config import ConfiguracaoConexao
from .tipos import InfoTipo, TipoColuna, familia_sql, tipo_sql

_TIPOS_TEXTO_PRECISAM_PREFIXO = ("text", "varchar", "char", "mediumtext", "longtext", "tinytext")

Logger = Callable[[str], None]


def criar_engine(config: ConfiguracaoConexao) -> Engine:
    return create_engine(config.url_sqlalchemy())


def _engine_do_servidor(config: ConfiguracaoConexao) -> Engine:
    """Engine conectado no servidor sem selecionar nenhum banco especifico,
    usado pra checar/criar o banco antes dele existir."""
    return create_engine(config.url_sqlalchemy(incluir_banco=False))


def testar_conexao(config: ConfiguracaoConexao) -> None:
    """Levanta uma excecao se nao conseguir conectar (com o banco selecionado);
    caso contrario, so retorna."""
    engine = criar_engine(config)
    with engine.connect() as conexao:
        conexao.execute(text("SELECT 1"))


def testar_conexao_servidor(config: ConfiguracaoConexao) -> None:
    """Levanta uma excecao se nao conseguir autenticar no servidor, sem
    selecionar nenhum banco especifico. Usa isso ANTES de perguntar sobre
    criar um banco nao existente, pra nao confundir "banco nao existe" com
    "host/usuario/senha errados"."""
    engine = _engine_do_servidor(config)
    with engine.connect() as conexao:
        conexao.execute(text("SELECT 1"))


def banco_existe(config: ConfiguracaoConexao) -> bool:
    """Verifica se o banco de dados indicado em `config.banco` ja existe no servidor."""
    engine = _engine_do_servidor(config)
    with engine.connect() as conexao:
        resultado = conexao.execute(text("SHOW DATABASES LIKE :nome"), {"nome": config.banco})
        return resultado.first() is not None


def criar_banco(config: ConfiguracaoConexao) -> None:
    """Cria o banco de dados indicado em `config.banco`, se ainda nao existir."""
    engine = _engine_do_servidor(config)
    with engine.begin() as conexao:
        conexao.execute(text(
            f"CREATE DATABASE IF NOT EXISTS `{config.banco}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci"
        ))


def gerar_nome_banco_generico() -> str:
    """Nome padrao sugerido quando o usuario nao informa um banco de dados."""
    return f"banco_{datetime.now():%Y%m%d_%H%M%S}"


_PADROES_ERRO_CONEXAO: list[tuple[re.Pattern, str]] = [
    (
        re.compile(r"1045|Access denied|auth_gssapi|caching_sha2"),
        "Usuário ou senha incorretos.",
    ),
    (
        re.compile(r"1049|Unknown database"),
        "O banco de dados informado não foi encontrado no servidor.",
    ),
    (
        re.compile(r"2003|Can.?t connect|10061|timed? ?out"),
        "Não foi possível alcançar o servidor. Confira o host, a porta, e se "
        "este computador tem acesso de rede até lá.",
    ),
]


def mensagem_amigavel(erro: Exception) -> str:
    """Traduz erros comuns de conexao pra uma mensagem clara em portugues,
    mantendo o erro tecnico original como detalhe pra quem quiser investigar."""
    texto = str(erro)
    for padrao, mensagem in _PADROES_ERRO_CONEXAO:
        if padrao.search(texto):
            return f"{mensagem}\n\nDetalhe técnico: {texto}"
    return texto


def _plano_indices(df: pd.DataFrame) -> list[tuple[str, bool]]:
    """Decide quais colunas devem ganhar indice, so olhando os dados da planilha
    (sem tocar no banco). Retorna uma lista de (nome_da_coluna, deve_ser_unico).

    Regra: a coluna `id` ganha indice unico se os valores dela forem realmente
    unicos (linha por linha); qualquer coluna terminada em `_id` ganha indice
    comum (convencao quase universal pra chave estrangeira)."""
    plano = []
    for coluna in df.columns:
        if coluna == "id":
            valores_unicos = df[coluna].dropna().is_unique
            plano.append((coluna, valores_unicos))
        elif coluna.endswith("_id"):
            plano.append((coluna, False))
    return plano


class TabelaRepository:
    """Encapsula as operacoes de DDL/DML que dependem de uma tabela especifica
    (criar, alterar colunas, truncar, contar, indexar) num unico ponto de
    acesso, pra quem usa nao precisar repassar engine+tabela em toda chamada.

    Operacoes que nao dependem de uma tabela (criar o banco, testar conexao)
    ficam fora daqui, como funcoes soltas no modulo."""

    def __init__(self, engine: Engine, tabela: str) -> None:
        self._engine = engine
        self._tabela = tabela

    def contar_linhas(self) -> int:
        with self._engine.connect() as conexao:
            return conexao.execute(text(f"SELECT COUNT(*) FROM `{self._tabela}`")).scalar()

    def truncar(self) -> bool:
        """Esvazia a tabela se ela existir. Retorna True se havia tabela pra esvaziar."""
        with self._engine.begin() as conexao:
            if not inspect(self._engine).has_table(self._tabela):
                return False
            conexao.execute(text(f"TRUNCATE TABLE `{self._tabela}`"))
            return True

    def garantir_colunas(
        self,
        tipos: dict[str, tuple[TipoColuna, InfoTipo]],
        corrigir_tipo_existente: bool,
        log: Logger = print,
    ) -> None:
        """Cria a tabela (com os tipos detectados) se ela nao existir, adiciona
        colunas que faltam, e - só quando `corrigir_tipo_existente` for True (ou
        seja, a tabela ja foi truncada antes, sem risco) - corrige o tipo de
        colunas existentes que estejam diferentes do tipo detectado agora."""
        inspector = inspect(self._engine)
        with self._engine.begin() as conexao:
            if not inspector.has_table(self._tabela):
                self._criar(conexao, tipos)
                log(f"Tabela '{self._tabela}' criada com {len(tipos)} colunas.")
                return

            colunas_existentes = {c["name"]: c["type"] for c in inspector.get_columns(self._tabela)}
            for coluna, (tipo, info) in tipos.items():
                sql_tipo = tipo_sql(tipo, info)
                if coluna not in colunas_existentes:
                    conexao.execute(text(
                        f"ALTER TABLE `{self._tabela}` ADD COLUMN `{coluna}` {sql_tipo} DEFAULT NULL"
                    ))
                    log(f"Coluna '{coluna}' adicionada em '{self._tabela}' como {sql_tipo}.")
                elif corrigir_tipo_existente:
                    tipo_atual = colunas_existentes[coluna]
                    if familia_sql(tipo_atual) != tipo:
                        conexao.execute(text(
                            f"ALTER TABLE `{self._tabela}` MODIFY COLUMN `{coluna}` {sql_tipo} DEFAULT NULL"
                        ))
                        log(f"Coluna '{coluna}' em '{self._tabela}' alterada de {tipo_atual} para {sql_tipo}.")

    def _criar(self, conexao, tipos: dict[str, tuple[TipoColuna, InfoTipo]]) -> None:
        definicoes = ",\n  ".join(
            f"`{coluna}` {tipo_sql(tipo, info)} DEFAULT NULL" for coluna, (tipo, info) in tipos.items()
        )
        conexao.execute(text(
            f"CREATE TABLE `{self._tabela}` (\n  {definicoes}\n) "
            "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci"
        ))

    def criar_indices_automaticos(self, df: pd.DataFrame, log: Logger = print) -> None:
        """Cria indices nas colunas de id (ver `_plano_indices`), sem mexer em
        nenhum dado. E' seguro rodar de novo (pula o que ja existe) e tolera
        falhar numa coluna especifica (ex: `id` que nao e' unica na pratica) sem
        interromper o restante."""
        inspector = inspect(self._engine)
        colunas_no_banco = {c["name"]: str(c["type"]) for c in inspector.get_columns(self._tabela)}
        indices_existentes = {indice["name"] for indice in inspector.get_indexes(self._tabela)}

        for coluna, deve_ser_unico in _plano_indices(df):
            if coluna not in colunas_no_banco:
                continue

            nome_indice = f"ix_{self._tabela}_{coluna}"
            if nome_indice in indices_existentes:
                continue

            tipo_coluna = colunas_no_banco[coluna].split("(")[0].strip().lower()
            precisa_prefixo = tipo_coluna in _TIPOS_TEXTO_PRECISAM_PREFIXO
            expressao_coluna = f"`{coluna}`(20)" if precisa_prefixo else f"`{coluna}`"
            tipo_indice = "UNIQUE INDEX" if deve_ser_unico else "INDEX"

            try:
                with self._engine.begin() as conexao:
                    conexao.execute(text(
                        f"ALTER TABLE `{self._tabela}` ADD {tipo_indice} `{nome_indice}` ({expressao_coluna})"
                    ))
                log(f"Índice criado: {self._tabela}.{coluna} ({tipo_indice}).")
            except OperationalError as erro:
                log(f"Não foi possível criar índice em {self._tabela}.{coluna} (seguindo sem ele): {erro}")
