@echo off
cd /d "%~dp0"
where pythonw >nul 2>nul
if %errorlevel% neq 0 (
    echo Python nao parece estar instalado ainda.
    echo Clique primeiro em "Instalar Programa.bat", depois tente de novo.
    pause
    exit /b
)
start "" pythonw "Importador.pyw"
