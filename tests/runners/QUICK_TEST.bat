@echo off
REM Quick Test Runner - Runs all tests without prompts
REM Usage: QUICK_TEST.bat

cls
color 0F

echo.
echo AttachmentLens - Quick Test Runner
echo ================================================================================
echo.

REM Change to project root directory
cd /d "%~dp0..\.."

REM Check and start Flask if needed
netstat -ano | findstr :5000 >nul 2>&1
if errorlevel 1 (
    echo Starting Flask app...
    start "Flask" python app.py
    timeout /t 3 /nobreak
)

echo Running all test suites...
echo.

REM Run all tests
python tests\runners\comprehensive_test.py & ^
python tests\runners\extended_tests.py & ^
python tests\runners\user_flow_tests.py

echo.
echo ================================================================================
echo Tests complete! Results in: test_runs\
echo View: test_runs\TESTS_FINAL_REPORT.md
echo ================================================================================
echo.
pause
