@echo off
REM AttachmentLens Test Runner for Windows
REM Runs all functional test suites and generates reports

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
for %%A in ("%SCRIPT_DIR%\..\..") do set "PROJECT_ROOT=%%~fA"
set "TEST_RUNS_DIR=%PROJECT_ROOT%\test_runs"

echo ============================================================
echo AttachmentLens Functional Test Suite
echo ============================================================
echo.

REM Create test_runs directory if needed
if not exist "%TEST_RUNS_DIR%" (
    mkdir "%TEST_RUNS_DIR%"
    echo [OK] Created test_runs directory
)

REM Check if -NoApp flag is set
set "NO_APP=0"
if "%~1"=="-NoApp" set "NO_APP=1"
if "%~1"=="--no-app" set "NO_APP=1"

REM Start Flask app if requested
if "%NO_APP%"=="0" (
    echo [INFO] Starting Flask app...
    echo [INFO] Flask will run in background
    echo.

    REM Start Flask in background
    cd /d "%PROJECT_ROOT%"
    start "Flask Server" python app.py

    REM Wait for Flask to start
    timeout /t 3 /nobreak

    echo [OK] Flask app started
    echo.
)

REM Run comprehensive tests
echo [1/2] Running comprehensive test suite ^(22 tests^)...
echo       Location: %SCRIPT_DIR%comprehensive_test.py
echo.

cd /d "%SCRIPT_DIR%"
python comprehensive_test.py
if errorlevel 1 (
    echo [ERROR] Comprehensive tests failed
)

echo.
echo [2/2] Running extended test suite ^(27 tests^)...
echo       Location: %SCRIPT_DIR%extended_tests.py
echo.

python extended_tests.py
if errorlevel 1 (
    echo [ERROR] Extended tests failed
)

echo.
echo ============================================================
echo Test Execution Complete
echo ============================================================
echo.
echo Test Results:
echo   Location: %TEST_RUNS_DIR%
echo.
echo Generated Files:
for %%F in ("%TEST_RUNS_DIR%\TEST_RUN_*.md") do (
    echo   - %%~nxF
)
echo   - TESTS_FINAL_REPORT.md
echo   - TEST_EXECUTION_SUMMARY.md
echo.

REM Stop Flask if we started it
if "%NO_APP%"=="0" (
    echo [INFO] Stopping Flask app...
    taskkill /FI "WINDOWTITLE eq Flask Server" /T /F >nul 2>&1
    echo [OK] Flask app stopped
)

echo.
echo Run tests again with: run_all_tests.bat
echo.
pause
