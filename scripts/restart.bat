@echo off
cd /d "%~dp0"
echo Rebuilding and restarting AttachmentLens...
docker compose up --build -d
echo.
echo Done! App is at http://localhost:5000
pause
