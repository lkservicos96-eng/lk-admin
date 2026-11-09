@echo off
echo ================================================
echo BACKUP DO PROJETO LK ADMIN - GPS EMPRESAS
echo ================================================
echo.

set DESTINO=%USERPROFILE%\Desktop\LK_Admin_GPS_Empresas

echo Criando pasta no Desktop...
if not exist "%DESTINO%" mkdir "%DESTINO%"

echo Copiando arquivos...
xcopy /E /I /Y "%~dp0*" "%DESTINO%"

echo.
echo ================================================
echo BACKUP CONCLUIDO!
echo ================================================
echo.
echo Arquivos salvos em:
echo %DESTINO%
echo.
echo Voce pode abrir essa pasta e guardar em um pendrive,
echo OneDrive, ou onde preferir.
echo.
pause
