from importador.planilha import normalizar_nome_coluna, resolver_nomes_duplicados


def test_normalizar_espacos_e_acentos():
    assert normalizar_nome_coluna("Nome do Produto") == "nome_do_produto"


def test_normalizar_simbolos():
    assert normalizar_nome_coluna("Preço (R$)") == "preco_r"


def test_normalizar_nome_vazio():
    assert normalizar_nome_coluna("") == "coluna"


def test_normalizar_comecando_com_digito():
    assert normalizar_nome_coluna("2025_vendas") == "c_2025_vendas"


def test_resolver_nomes_duplicados():
    colunas = ["id", "nome", "id"]
    assert resolver_nomes_duplicados(colunas) == ["id", "nome", "id_2"]


def test_resolver_nomes_sem_duplicata_fica_igual():
    colunas = ["a", "b", "c"]
    assert resolver_nomes_duplicados(colunas) == ["a", "b", "c"]
