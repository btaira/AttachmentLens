@echo off
cd /d "%~dp0\.."
echo Starting AttachmentLens...
docker compose up -d
echo.
echo Done! App is at http://localhost:5000
pause
