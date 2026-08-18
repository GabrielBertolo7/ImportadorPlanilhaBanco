import pandas as pd

from importador.banco import _plano_indices


def test_id_unico_vira_indice_unico():
    df = pd.DataFrame({"id": [1, 2, 3], "nome": ["a", "b", "c"]})
    plano = _plano_indices(df)
    assert plano == [("id", True)]


def test_id_repetido_nao_vira_unico():
    df = pd.DataFrame({"id": [1, 1, 2], "nome": ["a", "b", "c"]})
    plano = _plano_indices(df)
    assert plano == [("id", False)]


def test_colunas_terminadas_em_id_sempre_indice_comum():
    df = pd.DataFrame({"id": [1, 2], "pessoa_id": [10, 10], "familia_id": [5, 6]})
    plano = _plano_indices(df)
    assert ("pessoa_id", False) in plano
    assert ("familia_id", False) in plano


def test_colunas_sem_id_nao_entram_no_plano():
    df = pd.DataFrame({"nome_produto": ["a", "b"], "valor": [1, 2]})
    assert _plano_indices(df) == []


def test_id_com_nulos_ignora_nulos_na_checagem_de_unicidade():
    df = pd.DataFrame({"id": [1, None, 2]})
    plano = _plano_indices(df)
    assert plano == [("id", True)]
