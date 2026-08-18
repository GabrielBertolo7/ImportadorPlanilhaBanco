@echo off
setlocal
title Instalador - Importador de Planilhas

echo Verificando se o Python esta instalado...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Python nao foi encontrado neste computador. Instalando agora...
    echo (isso pode abrir uma janela do instalador do Python, aguarde terminar)
    echo.
    winget install --id Python.Python.3.12 --source winget --accept-source-agreements --accept-package-agreements
    echo.
    echo ==========================================================
    echo  IMPORTANTE: feche esta janela e clique de novo em
    echo  "Instalar Programa.bat" para continuar a instalacao.
    echo ==========================================================
    pause
    exit /b
)

echo Python encontrado.
echo Instalando as bibliotecas necessarias (pode levar 1-2 minutos)...
python -m pip install --upgrade pip
python -m pip install -r "%~dp0requisitos.txt"

echo.
echo ==========================================================
echo  Instalacao concluida! A partir de agora, use o atalho
echo  "Importar Planilha.bat" para abrir o programa.
echo ==========================================================
pause
