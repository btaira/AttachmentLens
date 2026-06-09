@echo off
REM Stop AttachmentLens Docker container

echo Stopping AttachmentLens...
docker-compose down

echo Done.
pause
