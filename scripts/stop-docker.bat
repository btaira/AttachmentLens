@echo off
cd /d "%~dp0\.."
echo Stopping AttachmentLens...
docker compose down
echo Done.
pause
