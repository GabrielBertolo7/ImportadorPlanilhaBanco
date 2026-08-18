"""Ponto de entrada do programa. Abre a janela do Importador de Planilhas.

Roda com 'pythonw Importador.pyw' (sem abrir janela de terminal), ou via o
atalho 'Importar Planilha.bat' que fica na mesma pasta.
"""
from importador.gui import executar

if __name__ == "__main__":
    executar()
