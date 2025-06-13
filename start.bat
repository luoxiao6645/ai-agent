@echo off
chcp 65001 >nul

echo Starting Multimodal AI Agent System...

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Check environment file
if not exist .env (
    echo WARNING: .env file not found, creating from template...
    copy .env.example .env
    echo Please edit .env file and add your API key
    echo Run this script again after editing
    pause
    exit /b 1
)

REM Create necessary directories
echo Creating necessary directories...
if not exist data mkdir data
if not exist logs mkdir logs
if not exist chroma_db mkdir chroma_db
if not exist chroma_data mkdir chroma_data

REM Build and start services
echo Building Docker images...
docker-compose build

echo Starting services...
docker-compose up -d

REM Wait for services to start
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check service status
echo Checking service status...
docker-compose ps

echo.
echo SUCCESS: Multimodal AI Agent System started!
echo.
echo Access URLs:
echo    - Web Interface: http://localhost:8501
echo    - ChromaDB: http://localhost:8000
echo.
echo Common commands:
echo    - View logs: docker-compose logs -f
echo    - Stop services: docker-compose down
echo    - Restart services: docker-compose restart
echo.
echo To modify configuration, edit .env file and restart services
echo.
pause
