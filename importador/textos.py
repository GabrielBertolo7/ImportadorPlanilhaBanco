"""Textos exibidos na interface grafica: titulos, rotulos e mensagens de dialogo.

Mantidos separados de gui.py pra nao misturar texto de interface com a logica
de construcao da tela, e pra facilitar revisar/alterar os textos sem precisar
mexer em codigo.
"""
from __future__ import annotations


class Janela:
    TITULO = "Importador de Planilhas para Banco de Dados"


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
