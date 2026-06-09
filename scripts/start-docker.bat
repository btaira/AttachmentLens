@echo off
REM Start AttachmentLens Docker container

echo Starting AttachmentLens...
docker-compose up -d

timeout /t 3 /nobreak

docker ps | find "attachmentlens" >/dev/null
if errorlevel 1 (
    echo ERROR: Container failed to start
    docker-compose logs
    pause
    exit /b 1
)

echo.
echo AttachmentLens is running at http://localhost:5000
echo.
pause
