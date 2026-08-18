import pandas as pd

from importador.tipos import (
    InfoTipo,
    TipoColuna,
    analisar_colunas,
    converter_valor,
    inferir_tipo_coluna,
)


def _serie(valores):
    return pd.Series(valores, dtype=object)


def test_inteiro_simples():
    tipo, info = inferir_tipo_coluna(_serie(["1", "2", "3000", "-5"]))
    assert tipo is TipoColuna.INTEIRO


def test_cep_com_zero_a_esquerda_fica_texto():
    tipo, _ = inferir_tipo_coluna(_serie(["05000000", "87030121", "01000000"]))
    assert tipo is TipoColuna.TEXTO


def test_chave_nfe_de_44_digitos_fica_texto():
    chave = "35250861531620001709550010008674471940601715"
    tipo, _ = inferir_tipo_coluna(_serie([chave, chave]))
    assert tipo is TipoColuna.TEXTO


def test_decimal_simples():
    tipo, info = inferir_tipo_coluna(_serie(["22.67", "0.10", "-5.50", "1000.00"]))
    assert tipo is TipoColuna.DECIMAL
    assert info.precisao == 6
    assert info.escala == 2


def test_data_sem_hora():
    tipo, info = inferir_tipo_coluna(_serie(["2025-08-25", "2025-09-01", "2026-01-16"]))
    assert tipo is TipoColuna.DATA
    assert info.formato == "%Y-%m-%d"


def test_data_com_hora():
    tipo, _ = inferir_tipo_coluna(
        _serie(["2025-08-25 00:00:00.000", "2025-09-01 16:09:11.000"])
    )
    assert tipo is TipoColuna.DATA_HORA


def test_texto_puro():
    tipo, _ = inferir_tipo_coluna(_serie(["FLEX - BARDAHL (200)", "PROTETIVO ROSA"]))
    assert tipo is TipoColuna.TEXTO


def test_mistura_de_texto_e_numero_fica_texto():
    tipo, _ = inferir_tipo_coluna(_serie(["1", "SEM GTIN", "3", "4"]))
    assert tipo is TipoColuna.TEXTO


def test_coluna_vazia_fica_texto():
    tipo, _ = inferir_tipo_coluna(_serie([None, None]))
    assert tipo is TipoColuna.TEXTO


def test_converter_valor_preserva_none():
    assert converter_valor(None, TipoColuna.INTEIRO, InfoTipo()) is None


def test_converter_valor_inteiro():
    assert converter_valor("42", TipoColuna.INTEIRO, InfoTipo()) == 42


def test_converter_valor_data():
    info = InfoTipo(formato="%Y-%m-%d")
    resultado = converter_valor("2025-08-25", TipoColuna.DATA, info)
    assert resultado.isoformat() == "2025-08-25"


def test_analisar_colunas_mensagens_de_log():
    df = pd.DataFrame({"id": ["1", "2"], "nome": ["a", "b"]})
    mensagens = []
    analisar_colunas(df, log=mensagens.append)
    assert any("id" in m and "bigint" in m for m in mensagens)
    assert any("nome" in m and "text" in m for m in mensagens)
