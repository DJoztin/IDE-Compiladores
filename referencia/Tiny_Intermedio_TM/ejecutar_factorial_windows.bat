@echo off
setlocal
cd /d "%~dp0"
if not exist tiny.exe (
    call compilar_windows.bat
    if errorlevel 1 exit /b 1
)
if not exist tm.exe (
    call compilar_windows.bat
    if errorlevel 1 exit /b 1
)
echo.
echo [1/2] Generando ejemplos\factorial.tm desde ejemplos\factorial.tny...
tiny.exe "ejemplos\factorial.tny"
if errorlevel 1 exit /b 1
echo.
echo [2/2] Abriendo la TM. Escribe g, luego el valor 5, y finalmente q.
echo.
tm.exe "ejemplos\factorial.tm"
