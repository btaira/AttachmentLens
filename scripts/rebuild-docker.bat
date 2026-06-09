@echo off
REM AttachmentLens Docker Rebuild and Restart Script
REM This script stops the current container, rebuilds the image, and starts it fresh

echo.
echo ========================================================
echo AttachmentLens Docker Rebuild and Restart
echo ========================================================
echo.

REM Check if Docker is running
docker ps >/dev/null 2>&1
if errorlevel 1 (
    echo ERROR: Docker daemon is not running.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [1/4] Stopping existing containers...
docker-compose down >/dev/null 2>&1
timeout /t 5 /nobreak

echo [2/4] Removing old image...
docker rmi attachmentlens:latest >/dev/null 2>&1

echo [3/4] Building new Docker image (this may take 1-2 minutes)...
docker build -t attachmentlens:latest . 
if errorlevel 1 (
    echo ERROR: Docker build failed
    pause
    exit /b 1
)

echo.
echo [4/4] Starting container...
docker-compose up -d

timeout /t 5 /nobreak

REM Check if container is running
docker ps | find "attachmentlens" >/dev/null
if errorlevel 1 (
    echo ERROR: Container failed to start
    docker-compose logs
    pause
    exit /b 1
)

echo.
echo ========================================================
echo SUCCESS! AttachmentLens is running
echo ========================================================
echo.
echo URL: http://localhost:5000
echo Username: admin
echo Password: admin
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak

start http://localhost:5000

echo.
echo To view logs: docker-compose logs -f
echo To stop: docker-compose down
echo.
pause
