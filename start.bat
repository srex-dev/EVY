@echo off
echo.
echo Starting EVY - Everyone's Voice, Everywhere, Everytime
echo ==========================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist "backend\.env" (
    echo Warning: backend\.env not found. Creating from example...
    (
        echo # Environment Configuration
        echo ENV=development
        echo.
        echo # Service Ports
        echo SMS_GATEWAY_PORT=8001
        echo MESSAGE_ROUTER_PORT=8002
        echo LLM_INFERENCE_PORT=8003
        echo RAG_SERVICE_PORT=8004
        echo PRIVACY_FILTER_PORT=8005
        echo API_GATEWAY_PORT=8000
        echo.
        echo # LLM Configuration
        echo LLM_PROVIDER=openai
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo DEFAULT_MODEL=gpt-4
        echo TINY_MODEL=gpt-3.5-turbo
        echo EMBEDDING_MODEL=text-embedding-ada-002
        echo.
        echo # Database Configuration
        echo DATABASE_URL=postgresql://evy:evy_password@postgres:5432/evy_db
        echo.
        echo # Vector Database
        echo CHROMA_PERSIST_DIR=/data/chroma
        echo.
        echo # Rate Limiting
        echo MAX_SMS_PER_MINUTE=10
        echo MAX_SMS_PER_HOUR=100
    ) > backend\.env
    echo Created backend\.env - Please set your OPENAI_API_KEY!
    echo.
)

echo Building Docker images...
docker-compose build

echo.
echo Starting services...
docker-compose up -d

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo EVY is starting up!
echo.
echo Service Endpoints:
echo    - Frontend Dashboard: http://localhost:3000
echo    - API Gateway:        http://localhost:8000
echo    - API Docs:           http://localhost:8000/docs
echo    - Prometheus:         http://localhost:9090
echo    - Grafana:            http://localhost:3001
echo.
echo View logs:    docker-compose logs -f
echo Stop services: docker-compose down
echo.
echo Happy coding!
echo.
pause


