@echo off
REM ================================================================
REM Health Data Pipeline - Environment Check Script
REM Autor: Caio Moreira
REM Descrição: Verifica pré-requisitos antes de executar o pipeline
REM ================================================================

echo.
echo ========================================
echo Health Data Pipeline - Environment Check
echo ========================================
echo.

REM Verificar Docker
echo [1/5] Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Docker not found! Please install Docker Desktop.
    goto :error
) else (
    docker --version
    echo [OK] Docker is installed
)
echo.

REM Verificar Docker Compose
echo [2/5] Checking Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Docker Compose not found!
    goto :error
) else (
    docker-compose --version
    echo [OK] Docker Compose is installed
)
echo.

REM Verificar Python
echo [3/5] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python not found! Please install Python 3.9+
    goto :error
) else (
    python --version
    echo [OK] Python is installed
)
echo.

REM Verificar arquivo de dados
echo [4/5] Checking data file...
if exist "data\LLCP2024ASC.asc" (
    echo [OK] Data file found: data\LLCP2024ASC.asc
) else (
    echo [!] Data file NOT found: data\LLCP2024ASC.asc
    echo [!] Please download from: https://www.cdc.gov/brfss/annual_data/annual_2024.html
)
echo.

REM Verificar estrutura de pastas
echo [5/5] Checking folder structure...
if exist "etl" (
    echo [OK] etl\ folder exists
) else (
    echo [X] etl\ folder missing
    goto :error
)

if exist "sql" (
    echo [OK] sql\ folder exists
) else (
    echo [X] sql\ folder missing
    goto :error
)

if exist "docs" (
    echo [OK] docs\ folder exists
) else (
    echo [X] docs\ folder missing
    goto :error
)

if exist "docker-compose.yml" (
    echo [OK] docker-compose.yml exists
) else (
    echo [X] docker-compose.yml missing
    goto :error
)
echo.

REM Verificar se Docker está rodando
echo [BONUS] Checking if Docker is running...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Docker is not running. Please start Docker Desktop.
) else (
    echo [OK] Docker is running
)
echo.

echo ========================================
echo All checks passed! You're ready to go!
echo ========================================
echo.
echo Next steps:
echo   1. docker-compose up -d
echo   2. pip install -r requirements.txt
echo   3. python etl\etl_brfss.py
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo [ERROR] Some checks failed!
echo ========================================
echo Please fix the issues above and try again.
echo.
pause
exit /b 1
