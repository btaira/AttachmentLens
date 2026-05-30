@echo off
echo Installing Flask...
python -m pip install flask --quiet
echo Starting server at http://localhost:5000
python app.py
pause
