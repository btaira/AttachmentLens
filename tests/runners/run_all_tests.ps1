# AttachmentLens Test Runner
# Runs all functional test suites and generates reports

param(
    [switch]$NoApp = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host "AttachmentLens Test Runner"
    Write-Host "Usage: .\run_all_tests.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -NoApp   Skip Flask app startup (app must be running)"
    Write-Host "  -Help    Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\run_all_tests.ps1              # Start Flask and run all tests"
    Write-Host "  .\run_all_tests.ps1 -NoApp       # Run tests only (app already running)"
    exit 0
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$TestRunsDir = Join-Path $ProjectRoot "test_runs"

Write-Host "=" * 60
Write-Host "AttachmentLens Functional Test Suite"
Write-Host "=" * 60
Write-Host ""

# Create test_runs directory if needed
if (-not (Test-Path $TestRunsDir)) {
    New-Item -ItemType Directory -Path $TestRunsDir | Out-Null
    Write-Host "[OK] Created test_runs directory"
}

# Start Flask app if requested
if (-not $NoApp) {
    Write-Host "[INFO] Starting Flask app..."
    Write-Host "[INFO] Note: Flask will run in background, press Ctrl+C to stop all processes"
    Write-Host ""

    # Start Flask in background
    $FlaskProcess = Start-Process -FilePath python -ArgumentList "app.py" `
        -WorkingDirectory $ProjectRoot `
        -PassThru -NoNewWindow

    # Wait for Flask to start
    Start-Sleep -Seconds 3

    Write-Host "[OK] Flask app started (PID: $($FlaskProcess.Id))"
    Write-Host ""
}

# Run comprehensive tests
Write-Host "[1/3] Running comprehensive test suite (21 tests)..."
Write-Host "      Location: $ScriptDir\comprehensive_test.py"
Write-Host ""

$CompResult = python (Join-Path $ScriptDir "comprehensive_test.py")

Write-Host ""
Write-Host "[2/3] Running extended test suite (27 tests)..."
Write-Host "      Location: $ScriptDir\extended_tests.py"
Write-Host ""

$ExtResult = python (Join-Path $ScriptDir "extended_tests.py")

Write-Host ""
Write-Host "[3/3] Running user flow test suite (7 flows, 70+ scenarios)..."
Write-Host "      Location: $ScriptDir\user_flow_tests.py"
Write-Host ""

$FlowResult = python (Join-Path $ScriptDir "user_flow_tests.py")

Write-Host ""
Write-Host "=" * 60
Write-Host "Test Execution Complete"
Write-Host "=" * 60
Write-Host ""
Write-Host "Test Results:"
Write-Host "  Location: $TestRunsDir"
Write-Host ""
Write-Host "Generated Files:"
Write-Host "  - TEST_RUN_$(Get-Date -Format 'yyyy-MM-dd').md"
Write-Host "  - TESTS_FINAL_REPORT.md"
Write-Host "  - TEST_EXECUTION_SUMMARY.md"
Write-Host ""

# Stop Flask if we started it
if (-not $NoApp) {
    Write-Host "[INFO] Stopping Flask app..."
    Stop-Process -Id $FlaskProcess.Id -Force -ErrorAction SilentlyContinue
    Write-Host "[OK] Flask app stopped"
}

Write-Host ""
Write-Host "Run tests again with: .\run_all_tests.ps1"
Write-Host ""
