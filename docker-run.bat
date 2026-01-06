@echo off
REM Easy Docker runner script for AI Hedge Fund (Windows)
REM Usage: docker-run.bat AAPL,MSFT

setlocal

echo.
echo [94m================================[0m
echo [94m  AI Hedge Fund Docker Runner[0m
echo [94m================================[0m
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [93mWarning: Docker is not installed or not in PATH![0m
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo [93mWarning: .env file not found![0m
    if exist .env.example (
        echo Creating .env from template...
        copy .env.example .env >nul
        echo [92mCreated .env file[0m
        echo [93mPlease edit .env and add your API keys before running again![0m
        exit /b 1
    ) else (
        echo [93mPlease create a .env file with your API keys[0m
        exit /b 1
    )
)

REM Build image if it doesn't exist
docker images | findstr /C:"ai-hedge-fund" >nul
if errorlevel 1 (
    echo [94mBuilding Docker image (first time, takes 3-5 minutes)...[0m
    docker-compose build
    echo [92mBuild complete![0m
    echo.
)

REM Get tickers from command line or use default
set TICKERS=%~1
if "%TICKERS%"=="" set TICKERS=AAPL

echo [92mAnalyzing: %TICKERS%[0m
echo.

REM Run the analysis
docker-compose run --rm hedge-fund --ticker %TICKERS% %2 %3 %4 %5 %6 %7 %8 %9

echo.
echo [92mAnalysis complete![0m
echo Check the output/ directory for results

endlocal

