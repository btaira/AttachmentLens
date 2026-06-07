# AttachmentLens Test Runner for PowerShell
# Usage: .\RUN_TESTS.ps1
# This script runs all three test suites from VS Code terminal

# Change to project root directory
Set-Location (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "AttachmentLens - Complete Test Runner" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Flask is running
Write-Host "[INFO] Checking if Flask is running on port 5000..." -ForegroundColor Yellow

$flask_running = netstat -ano | Select-String ":5000"
if (-not $flask_running) {
    Write-Host "[INFO] Flask not running, starting Flask app..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "app.py" -WindowStyle Minimized
    Start-Sleep -Seconds 3
    Write-Host "[OK] Flask app started" -ForegroundColor Green
} else {
    Write-Host "[OK] Flask is already running" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Running Test Suites" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Comprehensive
Write-Host "[1/3] Running Comprehensive Test Suite (22 tests)..." -ForegroundColor Cyan
Write-Host "      Location: tests\runners\comprehensive_test.py" -ForegroundColor Gray
Write-Host ""

python tests\runners\comprehensive_test.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Comprehensive tests failed" -ForegroundColor Red
} else {
    Write-Host "[SUCCESS] Comprehensive tests completed" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Test 2: Extended
Write-Host "[2/3] Running Extended Test Suite (27 tests)..." -ForegroundColor Cyan
Write-Host "      Location: tests\runners\extended_tests.py" -ForegroundColor Gray
Write-Host ""

python tests\runners\extended_tests.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Extended tests failed" -ForegroundColor Red
} else {
    Write-Host "[SUCCESS] Extended tests completed" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Test 3: User Flows
Write-Host "[3/3] Running User Flow Test Suite (70+ scenarios)..." -ForegroundColor Cyan
Write-Host "      Location: tests\runners\user_flow_tests.py" -ForegroundColor Gray
Write-Host ""

python tests\runners\user_flow_tests.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] User flow tests failed" -ForegroundColor Red
} else {
    Write-Host "[SUCCESS] User flow tests completed" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Test Execution Complete" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# List results
Write-Host "[INFO] Test results saved to: test_runs\" -ForegroundColor Yellow
Write-Host ""
Write-Host "Generated Files:" -ForegroundColor Cyan
Get-ChildItem -Path "test_runs" -Filter "TEST_RUN_*.md" | ForEach-Object {
    Write-Host "  - $($_.Name)"
}
Get-ChildItem -Path "test_runs" -Filter "*FINAL_REPORT.md" | ForEach-Object {
    Write-Host "  - $($_.Name)"
}

Write-Host ""
Write-Host "Quick View Commands:" -ForegroundColor Cyan
Write-Host '  - Final Report:   cat test_runs\TESTS_FINAL_REPORT.md | more' -ForegroundColor Gray
Write-Host '  - Comprehensive:  cat test_runs\TEST_RUN_COMPREHENSIVE_2026-06-07.md | more' -ForegroundColor Gray
Write-Host '  - Open Folder:    explorer test_runs' -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "Test Suite Complete!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
