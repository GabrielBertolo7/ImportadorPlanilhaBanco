"""Textos exibidos na interface grafica: titulos, rotulos, mensagens de dialogo
e de progresso.

Mantidos separados de gui.py pra nao misturar texto de interface com a logica
de construcao da tela, e pra facilitar revisar/alterar os textos sem precisar
mexer em codigo.

O padrao e' portugues. Com a variavel de ambiente IMPORTADOR_IDIOMA=en a
interface inteira fica em ingles (usado pra prints de portfolio).
"""
from __future__ import annotations

import os


class Janela:
    TITULO = "Importador de Planilhas para Banco de Dados"
    SUBTITULO = "Leve planilhas Excel ou CSV para o MySQL/MariaDB, com o tipo de cada coluna detectado sozinho."


class SecaoConexao:
    TITULO = "Conexão com o banco de dados"
    ROTULO_HOST = "Host (endereço do servidor):"
    ROTULO_PORTA = "Porta:"
    ROTULO_USUARIO = "Usuário:"
    ROTULO_SENHA = "Senha:"
    ROTULO_BANCO = "Nome do banco de dados:"
    BOTAO_TESTAR = "Testar conexão"


class SecaoPlanilha:
    TITULO = "Planilha a importar"
    BOTAO_SELECIONAR = "Selecionar planilha..."
    NENHUMA_PLANILHA = "Nenhuma planilha selecionada"
    ROTULO_TABELA = "Nome da tabela de destino:"
    OPCAO_SUBSTITUIR = "Substituir dados existentes na tabela"
    OPCAO_ADICIONAR = "Adicionar aos dados existentes (sem apagar nada)"
    BOTAO_IMPORTAR = "Importar"


class SecaoLog:
    TITULO = "Progresso"


class SeletorArquivo:
    TITULO = "Selecione a planilha"
    FILTRO_PLANILHAS = "Planilhas"
    FILTRO_TODOS = "Todos os arquivos"


class Dialogos:
    ATENCAO = "Atenção"
    CONEXAO = "Conexão"
    CONFIRMAR = "Confirmar"
    BANCO_NAO_INFORMADO = "Banco não informado"
    BANCO_NAO_ENCONTRADO = "Banco não encontrado"

    PREENCHA_DADOS_BANCO = "Preencha host, porta e usuário do banco."
    SELECIONE_PLANILHA = "Selecione uma planilha primeiro."
    INFORME_TABELA = "Informe o nome da tabela de destino."
    CONECTOU_COM_SUCESSO = "Conectou com sucesso!"

    @staticmethod
    def criar_banco_generico(nome_sugerido: str) -> str:
        return (
            "Nenhum banco de dados foi informado.\n\n"
            f"Deseja criar um novo banco chamado '{nome_sugerido}' agora?"
        )

    @staticmethod
    def criar_banco_inexistente(nome_banco: str) -> str:
        return (
            f"O banco de dados '{nome_banco}' não existe neste servidor.\n\n"
            "Deseja criar agora?"
        )

    @staticmethod
    def erro_conexao(detalhe: str) -> str:
        return f"Não foi possível conectar:\n\n{detalhe}"

    @staticmethod
    def erro_conexao_servidor(detalhe: str) -> str:
        return f"Não foi possível conectar ao servidor:\n\n{detalhe}"

    @staticmethod
    def confirmar_substituicao(tabela: str) -> str:
        return (
            f"Isso vai APAGAR os dados atuais da tabela '{tabela}' e recarregar com "
            "a planilha selecionada. Deseja continuar?"
        )


class Progresso:
    """Mensagens que aparecem na area de progresso durante a importacao."""

    ANALISANDO_TIPOS = "Analisando o tipo de cada coluna (numero, data ou texto)..."
    CONVERTENDO = "Convertendo os valores da planilha para os tipos corretos..."
    ENVIANDO = "Enviando os dados para o banco (pode demorar em planilhas grandes)..."
    CRIANDO_INDICES = "Criando índices nas colunas de id (acelera consultas e junções)..."
    ERRO = "ERRO"

    @staticmethod
    def lendo_planilha(caminho: object) -> str:
        return f"Lendo planilha: {caminho}"

    @staticmethod
    def linhas_encontradas(linhas: int, colunas: int) -> str:
        return f"{linhas} linhas e {colunas} colunas encontradas na planilha."

    @staticmethod
    def tabela_esvaziada(tabela: str) -> str:
        return f"Tabela '{tabela}' esvaziada antes de receber os dados novos."

    @staticmethod
    def concluido(tabela: str, total: int) -> str:
        return f"Importação concluída. A tabela '{tabela}' agora tem {total} linhas no total."

    @staticmethod
    def contagem_divergente(linhas: int, total: int) -> str:
        return (
            f"ATENÇÃO: a planilha tinha {linhas} linhas mas a tabela ficou com {total}. "
            "Confira antes de considerar concluído."
        )

    @staticmethod
    def tabela_criada(tabela: str, colunas: int) -> str:
        return f"Tabela '{tabela}' criada com {colunas} colunas."

    @staticmethod
    def coluna_adicionada(coluna: str, tabela: str, sql_tipo: str) -> str:
        return f"Coluna '{coluna}' adicionada em '{tabela}' como {sql_tipo}."

    @staticmethod
    def coluna_alterada(coluna: str, tabela: str, tipo_atual: object, sql_tipo: str) -> str:
        return f"Coluna '{coluna}' em '{tabela}' alterada de {tipo_atual} para {sql_tipo}."

    @staticmethod
    def indice_criado(tabela: str, coluna: str, tipo_indice: str) -> str:
        return f"Índice criado: {tabela}.{coluna} ({tipo_indice})."

    @staticmethod
    def indice_falhou(tabela: str, coluna: str, erro: object) -> str:
        return f"Não foi possível criar índice em {tabela}.{coluna} (seguindo sem ele): {erro}"


def _usar_ingles() -> None:
    """Troca todos os textos por ingles (IMPORTADOR_IDIOMA=en)."""
    Janela.TITULO = "Spreadsheet to Database Importer"
    Janela.SUBTITULO = "Load Excel or CSV files into MySQL/MariaDB, with each column type detected automatically."

    SecaoConexao.TITULO = "Database connection"
    SecaoConexao.ROTULO_HOST = "Host (server address):"
    SecaoConexao.ROTULO_PORTA = "Port:"
    SecaoConexao.ROTULO_USUARIO = "User:"
    SecaoConexao.ROTULO_SENHA = "Password:"
    SecaoConexao.ROTULO_BANCO = "Database name:"
    SecaoConexao.BOTAO_TESTAR = "Test connection"

    SecaoPlanilha.TITULO = "Spreadsheet to import"
    SecaoPlanilha.BOTAO_SELECIONAR = "Choose spreadsheet..."
    SecaoPlanilha.NENHUMA_PLANILHA = "No spreadsheet selected"
    SecaoPlanilha.ROTULO_TABELA = "Target table name:"
    SecaoPlanilha.OPCAO_SUBSTITUIR = "Replace the existing data in the table"
    SecaoPlanilha.OPCAO_ADICIONAR = "Append to the existing data (nothing is deleted)"
    SecaoPlanilha.BOTAO_IMPORTAR = "Import"

    SecaoLog.TITULO = "Progress"

    SeletorArquivo.TITULO = "Choose the spreadsheet"
    SeletorArquivo.FILTRO_PLANILHAS = "Spreadsheets"
    SeletorArquivo.FILTRO_TODOS = "All files"

    Dialogos.ATENCAO = "Attention"
    Dialogos.CONEXAO = "Connection"
    Dialogos.CONFIRMAR = "Confirm"
    Dialogos.BANCO_NAO_INFORMADO = "No database given"
    Dialogos.BANCO_NAO_ENCONTRADO = "Database not found"
    Dialogos.PREENCHA_DADOS_BANCO = "Fill in the database host, port and user."
    Dialogos.SELECIONE_PLANILHA = "Choose a spreadsheet first."
    Dialogos.INFORME_TABELA = "Enter the target table name."
    Dialogos.CONECTOU_COM_SUCESSO = "Connected successfully!"
    Dialogos.criar_banco_generico = staticmethod(
        lambda nome: f"No database was given.\n\nCreate a new database named '{nome}' now?"
    )
    Dialogos.criar_banco_inexistente = staticmethod(
        lambda nome: f"The database '{nome}' does not exist on this server.\n\nCreate it now?"
    )
    Dialogos.erro_conexao = staticmethod(lambda detalhe: f"Could not connect:\n\n{detalhe}")
    Dialogos.erro_conexao_servidor = staticmethod(
        lambda detalhe: f"Could not connect to the server:\n\n{detalhe}"
    )
    Dialogos.confirmar_substituicao = staticmethod(
        lambda tabela: f"This will DELETE the current data in table '{tabela}' and reload it "
        "from the selected spreadsheet. Continue?"
    )

    Progresso.ANALISANDO_TIPOS = "Detecting the type of each column (number, date or text)..."
    Progresso.CONVERTENDO = "Converting the spreadsheet values to the right types..."
    Progresso.ENVIANDO = "Sending the data to the database (large spreadsheets may take a while)..."
    Progresso.CRIANDO_INDICES = "Creating indexes on id columns (faster queries and joins)..."
    Progresso.ERRO = "ERROR"
    Progresso.lendo_planilha = staticmethod(lambda caminho: f"Reading spreadsheet: {caminho}")
    Progresso.linhas_encontradas = staticmethod(
        lambda linhas, colunas: f"{linhas} rows and {colunas} columns found in the spreadsheet."
    )
    Progresso.tabela_esvaziada = staticmethod(
        lambda tabela: f"Table '{tabela}' emptied before receiving the new data."
    )
    Progresso.concluido = staticmethod(
        lambda tabela, total: f"Import finished. Table '{tabela}' now has {total} rows in total."
    )
    Progresso.contagem_divergente = staticmethod(
        lambda linhas, total: f"WARNING: the spreadsheet had {linhas} rows but the table ended up with "
        f"{total}. Check it before calling it done."
    )
    Progresso.tabela_criada = staticmethod(
        lambda tabela, colunas: f"Table '{tabela}' created with {colunas} columns."
    )
    Progresso.coluna_adicionada = staticmethod(
        lambda coluna, tabela, sql_tipo: f"Column '{coluna}' added to '{tabela}' as {sql_tipo}."
    )
    Progresso.coluna_alterada = staticmethod(
        lambda coluna, tabela, tipo_atual, sql_tipo: f"Column '{coluna}' in '{tabela}' changed from "
        f"{tipo_atual} to {sql_tipo}."
    )
    Progresso.indice_criado = staticmethod(
        lambda tabela, coluna, tipo_indice: f"Index created: {tabela}.{coluna} ({tipo_indice})."
    )
    Progresso.indice_falhou = staticmethod(
        lambda tabela, coluna, erro: f"Could not create an index on {tabela}.{coluna} "
        f"(continuing without it): {erro}"
    )


if os.environ.get("IMPORTADOR_IDIOMA", "").lower() == "en":
    _usar_ingles()
