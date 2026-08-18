"""Monta a pasta 'dist' com o pacote pronto pra distribuir (copiar pra rede, etc).

Roda com: python empacotar.py

So inclui o que a pessoa que for usar o programa precisa (pacote 'importador',
ponto de entrada, instaladores/atalhos e guia de uso). Nao inclui os testes,
cache, nem a conexao.json de teste do desenvolvedor: esse arquivo e' pessoal
de cada maquina e e' recriado sozinho na primeira vez que o programa roda.
"""
from __future__ import annotations

import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DESTINO = RAIZ / "dist"

ARQUIVOS_A_COPIAR = [
    "Importador.pyw",
    "Instalar Programa.bat",
    "Importar Planilha.bat",
    "requisitos.txt",
    "GUIA_DE_USO.md",
]

PASTAS_A_COPIAR = ["importador"]

_IGNORAR = shutil.ignore_patterns("__pycache__", "*.pyc")


def montar() -> Path:
    if DESTINO.exists():
        shutil.rmtree(DESTINO)
    DESTINO.mkdir(parents=True)

    for nome in ARQUIVOS_A_COPIAR:
        shutil.copy2(RAIZ / nome, DESTINO / nome)

    for nome in PASTAS_A_COPIAR:
        shutil.copytree(RAIZ / nome, DESTINO / nome, ignore=_IGNORAR)

    return DESTINO


if __name__ == "__main__":
    destino = montar()
    print(f"Pacote pronto em: {destino}")
    print("Copie o CONTEUDO dessa pasta pra onde for distribuir (rede, pendrive, etc).")
