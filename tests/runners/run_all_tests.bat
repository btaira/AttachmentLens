@echo off
REM AttachmentLens Complete Test Suite Runner
REM Run this from the project root directory in VS Code terminal
REM This will run all three test suites and generate comprehensive reports

setlocal enabledelayedexpansion

REM Change to project root directory
cd /d "%~dp0..\.."

REM Set colors for output (if supported)
cls
color 0F

echo.
echo ================================================================================
echo AttachmentLens - Complete Test Suite Runner
echo ================================================================================
echo.
echo This script will:
echo   1. Start Flask app (if not running)
echo   2. Run Comprehensive Tests (21 tests)
echo   3. Run Extended Tests (27 tests)
echo   4. Run User Flow Tests (70+ scenarios)
echo   5. Generate final report
echo   6. Display results
echo.
echo ================================================================================
echo.

REM Check if Flask is already running
echo [INFO] Checking if Flask is running...
netstat -ano | findstr :5000 >nul 2>&1
if errorlevel 1 (
    echo [INFO] Flask not running, starting Flask app...
    start "Flask App" python app.py
    timeout /t 3 /nobreak
    echo [OK] Flask app started
) else (
    echo [OK] Flask is already running on port 5000
)

echo.
echo ================================================================================
echo Running Test Suites
echo ================================================================================
echo.

REM Test suite 1: Comprehensive
echo [1/3] Running Comprehensive Test Suite (21 tests)...
echo       Location: tests\runners\comprehensive_test.py
echo.

python tests\runners\comprehensive_test.py
if errorlevel 1 (
    echo [ERROR] Comprehensive tests failed with exit code !errorlevel!
) else (
    echo [SUCCESS] Comprehensive tests completed
)

echo.
echo ================================================================================
echo.

REM Test suite 2: Extended
echo [2/3] Running Extended Test Suite (27 tests)...
echo       Location: tests\runners\extended_tests.py
echo.

python tests\runners\extended_tests.py
if errorlevel 1 (
    echo [ERROR] Extended tests failed with exit code !errorlevel!
) else (
    echo [SUCCESS] Extended tests completed
)

echo.
echo ================================================================================
echo.

REM Test suite 3: User Flows
echo [3/3] Running User Flow Test Suite (70+ scenarios)...
echo       Location: tests\runners\user_flow_tests.py
echo.

python tests\runners\user_flow_tests.py
if errorlevel 1 (
    echo [ERROR] User flow tests failed with exit code !errorlevel!
) else (
    echo [SUCCESS] User flow tests completed
)

echo.
echo ================================================================================
echo Test Execution Complete
echo ================================================================================
echo.

REM Check for test results
echo [INFO] Test results location: test_runs\
echo.

echo Generated Files:
if exist "test_runs\TEST_RUN_2026-06-07.md" (
    echo   - TEST_RUN_2026-06-07.md
)
if exist "test_runs\TESTS_FINAL_REPORT.md" (
    echo   - TESTS_FINAL_REPORT.md
)
if exist "test_runs\TEST_EXECUTION_SUMMARY.md" (
    echo   - TEST_EXECUTION_SUMMARY.md
)
if exist "test_runs\TEST_RUN_COMPREHENSIVE_2026-06-07.md" (
    echo   - TEST_RUN_COMPREHENSIVE_2026-06-07.md
)

echo.
echo Summary:
echo --------
echo View results in: test_runs\ folder
echo Quick check: test_runs\TESTS_FINAL_REPORT.md
echo Detailed:   test_runs\TEST_RUN_COMPREHENSIVE_2026-06-07.md
echo.

echo ================================================================================
echo Test Suite Complete!
echo ================================================================================
echo.

REM Ask if user wants to view results
echo Options:
echo   [1] View TESTS_FINAL_REPORT.md
echo   [2] View comprehensive report
echo   [3] Open test_runs folder
echo   [4] Exit
echo.

set /p choice="Select option (1-4): "

if "!choice!"=="1" (
    if exist "test_runs\TESTS_FINAL_REPORT.md" (
        type test_runs\TESTS_FINAL_REPORT.md | more
    )
) else if "!choice!"=="2" (
    if exist "test_runs\TEST_RUN_COMPREHENSIVE_2026-06-07.md" (
        type test_runs\TEST_RUN_COMPREHENSIVE_2026-06-07.md | more
    )
) else if "!choice!"=="3" (
    start explorer test_runs
) else (
    echo Exiting...
)

echo.
echo Next run: RUN_ALL_TESTS.bat
echo.
pause
