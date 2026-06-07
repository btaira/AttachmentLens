# Test Runners

This folder contains the **test execution scripts** for AttachmentLens functional testing.

## Files

### Test Scripts
- `comprehensive_test.py` — Core functionality test suite (22 tests)
- `extended_tests.py` — Extended critical path tests (27 tests)
- `run_tests.py` — Playwright-based browser testing (legacy)

### Test Runners
- `run_all_tests.ps1` — PowerShell script for Windows (recommended)
- `run_all_tests.bat` — Batch file for Windows

## Quick Start

### Option 1: PowerShell (Recommended for Windows)

```powershell
# Run all tests (starts Flask automatically)
.\run_all_tests.ps1

# Run tests only (Flask already running)
.\run_all_tests.ps1 -NoApp

# Show help
.\run_all_tests.ps1 -Help
```

### Option 2: Batch File

```cmd
REM Run all tests (starts Flask automatically)
run_all_tests.bat

REM Run tests only (Flask already running) - pass -NoApp argument
run_all_tests.bat -NoApp
```

### Option 3: Manual (Python Direct)

```bash
# Start Flask app
python app.py &

# Run comprehensive tests
python comprehensive_test.py

# Run extended tests
python extended_tests.py
```

## Test Suites

### Comprehensive Test Suite (22 tests)
**File**: `comprehensive_test.py`  
**Duration**: ~2 minutes  
**Coverage**:
- Authentication (login, registration, logout, validation)
- Library operations (home page, search, categories)
- Post management (view, favorite, read, edit, delete)
- Insights (create, update, read)
- Data import (JSON upload, validation)
- Export & backup (collections, full backup)
- Statistics API

**Run individually**:
```bash
python comprehensive_test.py
```

### Extended Test Suite (27 tests)
**File**: `extended_tests.py`  
**Duration**: ~2 minutes  
**Coverage**:
- Input validation (empty fields, duplicates, password length)
- Auth guard protection (unauthorized access)
- Multi-user operations (user switching, isolation)
- Library features (sorting, filtering)
- Import edge cases (non-array payloads, invalid JSON)
- Post revisions (edit, revert, clear)
- Advanced features (AI insights, modeled posts, bulk label)

**Run individually**:
```bash
python extended_tests.py
```

## Test Results

### Output Locations
- **Test Reports**: `../../test_runs/` folder
- **Report Files**:
  - `TEST_RUN_YYYY-MM-DD.md` — Detailed test results
  - `TESTS_FINAL_REPORT.md` — Consolidated final report
  - `TEST_EXECUTION_SUMMARY.md` — Executive summary

### Test Report Format
All test run files include:
- **TEST RUN DATE** in format `YYYY-MM-DD`
- **Test Start Time** and **End Time** (UTC)
- **Total Duration**
- **Complete test results** with Pass/Fail status
- **Feature-by-feature breakdown**
- **Failure analysis** with recommendations

## Requirements

### Python Packages
```bash
pip install requests playwright
```

### Flask App
The app must be running on `http://localhost:5000` before running tests.

```bash
python app.py
```

### Playwright (Optional)
Only needed for `run_tests.py`:
```bash
pip install playwright
playwright install chromium
```

## Test Execution Flow

```
Start Test Runner
    ↓
[Optional] Start Flask app
    ↓
Run Comprehensive Tests (22 tests)
    ↓
Run Extended Tests (27 tests)
    ↓
Generate Test Reports
    ↓
[Optional] Stop Flask app
    ↓
Display Results & Recommendations
    ↓
End
```

## Expected Output

```
============================================================
AttachmentLens Functional Test Suite
============================================================

[INFO] Starting Flask app...
[OK] Flask app started

[1/2] Running comprehensive test suite (22 tests)...
[PASS] AL-FUNC-001: Pass
[PASS] AL-FUNC-002: Pass
...
Test Summary: 21/22 passed

[2/2] Running extended test suite (27 tests)...
[PASS] AL-FUNC-004: Pass
...
Extended Tests Summary: 27/27 passed

============================================================
Test Execution Complete
============================================================

Test Results:
  Location: ../../test_runs/

Generated Files:
  - TEST_RUN_2026-06-07.md
  - TESTS_FINAL_REPORT.md
  - TEST_EXECUTION_SUMMARY.md
```

## Troubleshooting

### Port Already in Use
If Flask can't start because port 5000 is in use:
```bash
# Kill existing Flask process
taskkill /IM python.exe /F

# Or use different port
set FLASK_PORT=5001
python app.py
```

### Tests Fail with Connection Error
- Ensure Flask is running: `http://localhost:5000/login`
- Check that the database file exists: `posts.db`
- Verify Python can connect: `python -m requests --version`

### Test Reports Not Generated
- Check write permissions to `test_runs/` folder
- Ensure `test_runs/` folder exists (created automatically)
- Check Python console for error messages

### Playwright Installation Issues
If using `run_tests.py`, install browser:
```bash
playwright install chromium
```

## Test Metrics

### Overall
- **Total Tests**: 49
- **Success Rate**: 98%+ typical
- **Coverage**: 8 feature categories
- **Execution Time**: ~5 minutes

### By Priority
- **P0 (Critical)**: 15 tests
- **P1 (Major)**: 18 tests
- **P2 (Normal)**: 16 tests

### By Feature
| Feature | Tests | Pass Rate |
|---------|-------|-----------|
| Authentication | 8 | 100% |
| Library & Search | 6 | 100% |
| Post Management | 13 | 100% |
| Import | 5 | 100% |
| Insights | 6 | 100% |
| Export & Stats | 5 | 80% |
| Multi-User | 2 | 100% |
| UI Features | 3 | 100% |

## Next Steps

After running tests:
1. Review test reports in `../../test_runs/`
2. Check `TESTS_FINAL_REPORT.md` for summary
3. Address any failures listed in reports
4. Re-run tests after fixes to verify

## Advanced Usage

### Run Tests with Custom Database
```bash
# Use different database
set DB_PATH=test_db.db
python comprehensive_test.py
```

### Run Specific Test Suite Only
```bash
# Just comprehensive tests
python comprehensive_test.py

# Just extended tests
python extended_tests.py
```

### Debug Test Failures
```bash
# Run with Python verbose mode
python -u comprehensive_test.py

# Check Flask logs
tail -f flask.log  # On Linux/Mac
type flask.log     # On Windows
```

## Support

For test framework issues:
1. Check `tests/README.md` for general information
2. Review test report recommendations
3. Check Flask app logs: `python app.py 2>&1 | tee app.log`
4. Verify database connectivity: `python -c "import sqlite3; sqlite3.connect('posts.db')"`

---

**Last Updated**: 2026-06-07  
**Test Framework**: Python requests  
**Status**: Active - Ready to use
