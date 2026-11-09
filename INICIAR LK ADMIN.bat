@echo off
title LK admin - GPS Empresas
cd /d "%~dp0"

echo ============================================================
echo    LK admin - GPS Empresas
echo    Sistema de busca de empresas com processos
echo ============================================================
echo.

rem --- Procura o Python no computador ---
set "PYCMD="
py -3 --version >nul 2>&1
if %errorlevel%==0 set "PYCMD=py -3"
if defined PYCMD goto tem_python

python --version >nul 2>&1
if %errorlevel%==0 set "PYCMD=python"
if defined PYCMD goto tem_python

echo [ERRO] Python nao foi encontrado neste computador.
echo.
echo Solucao: instale o Python em https://www.python.org/downloads/
echo IMPORTANTE: na primeira tela da instalacao, marque a caixinha
echo "Add Python to PATH" antes de clicar em "Install Now".
echo Depois rode este arquivo de novo.
echo.
pause
exit /b 1

:tem_python
echo Python encontrado.
echo.

rem --- Verifica se o Flask esta instalado; instala se faltar ---
%PYCMD% -c "import flask, flask_cors" >nul 2>&1
if %errorlevel%==0 goto tem_flask

echo Primeira execucao: instalando o Flask (aguarde um minuto)...
%PYCMD% -m pip install --quiet flask flask-cors
if %errorlevel%==0 goto tem_flask

echo.
echo [ERRO] Nao consegui instalar o Flask.
echo Verifique sua internet e rode este arquivo de novo.
echo.
pause
exit /b 1

:tem_flask
echo Tudo pronto! Iniciando o servidor...
echo O navegador vai abrir automaticamente em http://localhost:5000
echo.
echo NAO FECHE ESTA JANELA enquanto estiver usando o sistema.
echo Para encerrar: feche esta janela ou aperte CTRL+C.
echo.

%PYCMD% servidor_web.py

echo.
echo O servidor foi encerrado. Ate a proxima!
pause
