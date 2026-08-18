import re

from importador.banco import gerar_nome_banco_generico, mensagem_amigavel
from importador.config import ConfiguracaoConexao


def test_nome_gerado_tem_formato_esperado():
    nome = gerar_nome_banco_generico()
    assert re.fullmatch(r"banco_\d{8}_\d{6}", nome)


def test_url_sem_banco_nao_tem_nome_de_banco():
    config = ConfiguracaoConexao(
        host="127.0.0.1", porta="3306", usuario="root", senha="x", banco="meu_banco"
    )
    url_completa = config.url_sqlalchemy()
    url_sem_banco = config.url_sqlalchemy(incluir_banco=False)
    assert "meu_banco" in url_completa
    assert "meu_banco" not in url_sem_banco


def test_mensagem_amigavel_senha_incorreta():
    erro = Exception("(pymysql.err.OperationalError) (1045, \"Access denied for user 'root'@'x'\")")
    assert "senha incorretos" in mensagem_amigavel(erro)


def test_mensagem_amigavel_auth_gssapi():
    erro = Exception(
        "(pymysql.err.OperationalError) (2059, \"Authentication plugin 'auth_gssapi_client' not configured\")"
    )
    assert "senha incorretos" in mensagem_amigavel(erro)


def test_mensagem_amigavel_banco_inexistente():
    erro = Exception('(pymysql.err.OperationalError) (1049, "Unknown database \'x\'")')
    assert "não foi encontrado" in mensagem_amigavel(erro)


def test_mensagem_amigavel_host_inalcancavel():
    erro = Exception("(pymysql.err.OperationalError) (2003, \"Can't connect to MySQL server\")")
    assert "alcançar o servidor" in mensagem_amigavel(erro)


def test_mensagem_amigavel_erro_desconhecido_mantem_texto_original():
    erro = Exception("algum erro totalmente diferente")
    assert mensagem_amigavel(erro) == "algum erro totalmente diferente"
