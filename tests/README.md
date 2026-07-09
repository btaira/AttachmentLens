# Tests

This directory contains **functional test cases and test execution infrastructure** for AttachmentLens.

## Directory Structure

- `functional/` — Manual test case definitions
  - `FUNCTIONAL_TEST_CASES.md` — Canonical test cases by feature (definitions)
  - `TEST_RUN_TEMPLATE.md` — Template for documenting test results
- `runners/` — Test execution scripts
  - `comprehensive_test.py` — Core functionality test suite (21 tests)
  - `extended_tests.py` — Extended critical path tests (27 tests)
  - `run_tests.py` — Playwright-based browser testing

## Test Run Requirements

All test run files **MUST** include:
- **TEST RUN DATE** in format: `YYYY-MM-DD` (e.g., `2026-06-07`)
- **Test Start Time** in UTC (e.g., `08:31 UTC`)
- **Test End Time** in UTC (e.g., `08:35 UTC`)
- **Test Duration** (e.g., `~5 minutes`)
- **Run ID** with format: `TEST-YYYYMMDD-IDENTIFIER` (e.g., `TEST-20260607-COMPREHENSIVE`)

### Example Header Format
```markdown
---
TEST RUN DATE: 2026-06-07
Test Start Time: 08:31 UTC
Test End Time: 08:35 UTC
Total Duration: ~5 minutes
Run ID: TEST-20260607-COMPREHENSIVE
---
```

## Recommended Workflow

1. **Test Cases**: Keep `functional/FUNCTIONAL_TEST_CASES.md` in the main branch (versioned with the app).

2. **Test Execution**: 
   - Run test scripts from `runners/` directory
   - Tests log to stdout and generate markdown reports
   
3. **Test Results**: 
   - All test run files go in `../test_runs/` folder (see `.gitignore`)
   - File naming: `TEST_RUN_YYYY-MM-DD.md`
   - Include all required metadata (see above)
   - File format: Markdown with tables for results

4. **Test Reports**:
   - `TESTS_FINAL_REPORT.md` — Consolidated final results
   - `TEST_EXECUTION_SUMMARY.md` — Executive summary
   - `TEST_RUN_YYYY-MM-DD.md` — Detailed test results

## How to Run Tests

```bash
# Install dependencies
pip install requests playwright

# Start the Flask app
python app.py

# In another terminal, run test suites
python tests/runners/comprehensive_test.py    # Core functionality (21 tests)
python tests/runners/extended_tests.py        # Extended paths (27 tests)

# Results saved to test_runs/ folder
```

## Test Coverage

- **48 test cases** across 8 feature categories
- **98%+ success rate** typical
- Coverage includes:
  - Authentication & sessions
  - Library & search
  - Post management (CRUD)
  - Data import/export
  - Insights & analysis
  - Validation & error handling
  - Multi-user support

## Test Files Organization

```
project-root/
├── tests/
│   ├── README.md (this file)
│   ├── functional/
│   │   ├── FUNCTIONAL_TEST_CASES.md
│   │   └── TEST_RUN_TEMPLATE.md
│   └── runners/
│       ├── comprehensive_test.py
│       ├── extended_tests.py
│       └── run_tests.py
└── test_runs/                    (git ignored)
    ├── TEST_RUN_2026-06-07.md
    ├── TESTS_FINAL_REPORT.md
    └── TEST_EXECUTION_SUMMARY.md
```

