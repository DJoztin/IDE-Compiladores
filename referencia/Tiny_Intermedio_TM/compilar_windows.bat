@echo off
setlocal
cd /d "%~dp0"
where gcc >nul 2>nul
if errorlevel 1 (
    echo ERROR: No se encontro GCC en PATH.
    echo En VS Code abre la terminal de MSYS2 UCRT64, o configura PATH a ...\msys64\ucrt64\bin.
    exit /b 1
)
echo [1/2] Compilando el compilador TINY...
gcc -std=c11 -O2 -Wall -Wextra -Wpedantic main.c util.c scan.c parse.c symtab.c analyze.c code.c cgen.c intermedio.c -o tiny.exe
if errorlevel 1 (
    echo ERROR al compilar TINY.
    exit /b 1
)
echo [2/2] Compilando el simulador TM...
gcc -std=c11 -O2 -Wall -Wextra -Wpedantic tm.c -o tm.exe
if errorlevel 1 (
    echo ERROR al compilar TM.
    exit /b 1
)
echo.
echo COMPILACION CORRECTA: tiny.exe y tm.exe
exit /b 0
