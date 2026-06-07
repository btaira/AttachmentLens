@echo off
cd /d "%~dp0"
echo.
echo === Attachment Lens — Git Push ===
echo.
git add README.md TODO.md templates/ai_insights.html templates/base.html templates/import.html templates/insights.html app.py
git status
echo.
git commit -m "Add README, TODO roadmap; AI Insights history, feedback, delete key; nav reorder; likes fix"
echo.
git push
echo.
echo === Done! Press any key to close ===
pause
