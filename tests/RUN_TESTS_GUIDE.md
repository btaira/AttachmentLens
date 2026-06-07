# How to Run Tests from VS Code

**Quick Reference**: Run tests in VS Code terminal with one command

---

## Option 1: Quick Test (Fastest)

### From VS Code Terminal

1. **Open Terminal** in VS Code
   - Press `Ctrl + `` (backtick) or `Terminal → New Terminal`

2. **Run Quick Test**
   ```cmd
   tests\runners\QUICK_TEST.bat
   ```

3. **What It Does**
   - ✓ Starts Flask (if not running)
   - ✓ Runs all 3 test suites
   - ✓ Shows results when complete
   - ✓ Takes ~4 minutes

### Result
```
AttachmentLens - Quick Test Runner
================================================================================

Running all test suites...

[Tests run in background...]

================================================================================
Tests complete! Results in: test_runs\
View: test_runs\TESTS_FINAL_REPORT.md
================================================================================
```

---

## Option 2: Full Test Runner (Interactive)

### From VS Code Terminal

1. **Open Terminal** in VS Code

2. **Run Full Test Suite**
   ```cmd
   tests\runners\RUN_ALL_TESTS.bat
   ```

3. **What It Does**
   - ✓ Checks if Flask is running
   - ✓ Starts Flask if needed
   - ✓ Shows progress for each test suite
   - ✓ Lists generated report files
   - ✓ Offers menu to view reports
   - ✓ Takes ~4-5 minutes

### Interactive Menu
```
Options:
   [1] View TESTS_FINAL_REPORT.md
   [2] View comprehensive report
   [3] Open test_runs folder
   [4] Exit

Select option (1-4): _
```

---

## Option 3: Individual Test Suites

### Run Only Comprehensive Tests
```cmd
python tests\runners\comprehensive_test.py
```
**Duration**: ~2 minutes | **Tests**: 22

### Run Only Extended Tests
```cmd
python tests\runners\extended_tests.py
```
**Duration**: ~2 minutes | **Tests**: 27

### Run Only User Flow Tests
```cmd
python tests\runners\user_flow_tests.py
```
**Duration**: ~2 minutes | **Tests**: 70+

---

## Step-by-Step: Running from VS Code

### 1. Open Project in VS Code
```
File → Open Folder → Select AttachmentLens folder
```

### 2. Open Integrated Terminal
```
Ctrl + ` (backtick)
or
Terminal → New Terminal
```

You'll see terminal at bottom of VS Code:
```
PS C:\Users\btair\OneDrive\Documents\GitHub\AttachmentLens>
```

### 3. Run Tests
```cmd
QUICK_TEST.bat
```

### 4. Watch Progress
The terminal will show:
```
AttachmentLens - Quick Test Runner
AttachmentLens Functional Test Suite
Started: 2026-06-07 10:26:25
============================================================
[PASS] AL-FUNC-001: Pass
[PASS] AL-FUNC-002: Pass
...
```

### 5. View Results
When complete, navigate to `test_runs\` folder in VS Code:
- Open Explorer (Ctrl+Shift+E)
- Click on `test_runs` folder
- Click on reports to view

---

## Common Scenarios

### End of Day Testing
```cmd
QUICK_TEST.bat
```
Quick run of all tests before committing code.

### Full Quality Check
```cmd
RUN_ALL_TESTS.bat
```
Interactive mode with detailed results and report options.

### Debug Single Suite
```cmd
python tests\runners\user_flow_tests.py
```
Run just the user flow tests to debug specific workflows.

### Manual Test Run
```cmd
REM Start Flask manually
python app.py

REM In another terminal, run tests
python tests\runners\comprehensive_test.py
```

---

## Troubleshooting

### "Flask app failed to start"
- **Solution**: Flask is already running on port 5000
- **Fix**: Close other Flask processes or specify different port

### "Tests fail with connection error"
- **Solution**: Flask not running or not responding
- **Fix**: Run `python app.py` in separate terminal first

### "Permission denied" error
- **Solution**: Script execution policy issue
- **Fix**: Run VS Code as Administrator

### "Module not found" error
- **Solution**: Required Python packages not installed
- **Fix**: Run `pip install requests` in terminal

---

## Test Reports

### Location
```
test_runs\
```

### Key Reports
1. **TESTS_FINAL_REPORT.md** - Summary of all tests
2. **TEST_RUN_COMPREHENSIVE_2026-06-07.md** - Detailed results
3. **TEST_EXECUTION_SUMMARY.md** - Executive summary
4. **TEST_RUN_2026-06-07.md** - Original functional test results

### How to View in VS Code
```
1. Open Explorer (Ctrl+Shift+E)
2. Navigate to test_runs folder
3. Click on report file
4. Read in editor or preview
```

---

## Keyboard Shortcuts in Terminal

| Shortcut | Action |
|----------|--------|
| `Ctrl + C` | Stop running test |
| `Ctrl + `` | Toggle terminal |
| `Clear` | Clear terminal screen |
| `Ctrl + L` | Clear terminal (PowerShell) |
| `Ctrl + Shift + E` | Open Explorer |

---

## Sample Test Run Output

```
============================================================
AttachmentLens Functional Test Suite
Started: 2026-06-07 10:26:25
============================================================

[PASS] AL-FUNC-001: Login happy path
[PASS] AL-FUNC-002: Login invalid credentials
[PASS] AL-FUNC-003: Registration happy path
...
[FAIL] AL-FUNC-064: Stats dashboard HTTP 500
...

============================================================
Test Summary: 21/22 passed
============================================================

[SUCCESS] Test results saved to test_runs\TEST_RUN_2026-06-07.md
```

---

## Summary

### Quick Test (Recommended)
```
QUICK_TEST.bat
```
- Fastest option
- Runs all tests
- Shows results in ~4 minutes
- Perfect for end-of-session testing

### Full Test (For Detailed Review)
```
RUN_ALL_TESTS.bat
```
- Interactive menu
- View reports directly from terminal
- Browse test results
- Option to open test_runs folder

### Individual Suites
```
python tests\runners\comprehensive_test.py
python tests\runners\extended_tests.py
python tests\runners\user_flow_tests.py
```
- For debugging specific test suites
- Faster if you only need certain tests

---

## Pro Tips

### 1. Run in Background
Keep terminal open and run tests while continuing development:
```
QUICK_TEST.bat
```

### 2. Schedule Regular Runs
Add to your end-of-day routine:
- Run tests
- Review any failures
- Commit code

### 3. Compare Reports
Compare consecutive test runs to track quality:
- `TEST_RUN_2026-06-07.md`
- `TEST_RUN_2026-06-08.md`

### 4. Share Results
Reports are in Markdown format, easy to share:
- Email test report
- Commit to git
- Share in Slack

---

## Next Steps

1. **First Time Setup**
   - Open VS Code terminal
   - Run: `QUICK_TEST.bat`
   - Review results in `test_runs\`

2. **Regular Testing**
   - Run `QUICK_TEST.bat` before committing
   - Check for new issues in reports
   - Keep test results for trending

3. **Debug Issues**
   - Run specific test suite if issues found
   - Review detailed report
   - Check Flask logs if tests fail

---

## Questions?

Check these documents for more info:
- `QUICK_START_TESTS.md` - Getting started guide
- `USER_FLOWS_SUMMARY.md` - Complete test reference
- `TEST_ORGANIZATION_SUMMARY.md` - Test architecture
- `tests/README.md` - Test framework overview

---

**Created**: 2026-06-07  
**Status**: Ready to use
