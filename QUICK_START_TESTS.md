# Quick Start - Running AttachmentLens Tests

**Last Updated**: 2026-06-07

---

## ⚡ 30-Second Quick Start

### Windows (Command Prompt) - Quickest ⭐
```cmd
tests\runners\QUICK_TEST.bat
```

### Windows (Full Featured)
```cmd
tests\runners\RUN_ALL_TESTS.bat
```

### Windows (PowerShell)
```powershell
.\tests\runners\RUN_TESTS.ps1
```

### Linux/Mac (Manual)
```bash
python app.py &
python tests/runners/comprehensive_test.py
python tests/runners/extended_tests.py
```

---

## 📋 What You'll Get

After running tests:
- **49 test cases** executed automatically
- **~5 minute** execution time
- **Test reports** in `test_runs/` folder:
  - `TEST_RUN_2026-06-07.md` - Detailed results
  - `TESTS_FINAL_REPORT.md` - Final report
  - `TEST_EXECUTION_SUMMARY.md` - Executive summary

---

## 📂 Test File Locations

```
tests/
├── functional/              (Test case definitions)
│   ├── FUNCTIONAL_TEST_CASES.md
│   └── USER_FLOW_TEST_CASES.md      (NEW - End-to-end flows)
└── runners/                 (Test execution scripts)
    ├── comprehensive_test.py
    ├── extended_tests.py
    ├── user_flow_tests.py           (NEW - Flow testing)
    ├── run_all_tests.ps1    ← Run this
    └── run_all_tests.bat    ← Or this
```

**Results go to**: `test_runs/` (created automatically)

### Test Case Documents
- **FUNCTIONAL_TEST_CASES.md** - Individual feature test cases (49 tests)
- **USER_FLOW_TEST_CASES.md** - End-to-end user journey tests (70+ scenarios)

---

## 📖 Documentation

- **[tests/README.md](tests/README.md)** - Test framework overview
- **[tests/runners/README.md](tests/runners/README.md)** - How to run tests
- **[test_runs/README.md](test_runs/README.md)** - Test results format
- **[TEST_ORGANIZATION_SUMMARY.md](TEST_ORGANIZATION_SUMMARY.md)** - Complete organization guide

---

## ✅ Test Coverage

### Functional Test Cases (49 tests)
| Category | Tests | Status |
|----------|-------|--------|
| Authentication | 8 | ✓ 100% |
| Library & Search | 6 | ✓ 100% |
| Post Management | 13 | ✓ 100% |
| Data Import | 5 | ✓ 100% |
| Insights | 6 | ✓ 100% |
| Export & Backup | 5 | ⚠ 80% |
| Multi-User | 2 | ✓ 100% |
| UI Features | 3 | ✓ 100% |
| **SUBTOTAL** | **49** | **98%** |

### User Flow Test Cases (70+ scenarios)
| Flow | Steps | Scenarios | Status |
|------|-------|-----------|--------|
| Post Import | 5 | 10+ | Ready |
| Insights Creation | 5 | 11+ | Ready |
| AI Analysis | 8 | 12+ | Ready |
| Multi-User Collab | 6 | 11+ | Ready |
| Post Organization | 8 | 13+ | Ready |
| AI Generation | 5 | 10+ | Ready |
| Export & Backup | 9 | 14+ | Ready |
| **TOTAL** | **46** | **70+** | ✓ |

**Combined Total**: 119+ test scenarios across all categories

---

## ⚙️ Requirements

- Python 3.12+
- Flask (auto-started by runner scripts)
- sqlite3 (for posts.db)

### Install Test Dependencies
```bash
pip install requests
```

---

## 🔍 View Test Results

### Latest Results
```bash
cat test_runs/TESTS_FINAL_REPORT.md
```

### Detailed Results (2026-06-07)
```bash
cat test_runs/TEST_RUN_2026-06-07.md
```

### All Test Runs
```bash
ls -lh test_runs/TEST_RUN_*.md
```

---

## ⚠️ Known Issues

**Issue**: Stats Dashboard (AL-FUNC-064)
- **Status**: HTTP 500 error
- **Impact**: Minor - stats API works, dashboard needs fix
- **Workaround**: Use `/api/stats` endpoint directly

---

## 🚀 Typical Workflow

1. **Run Tests**
   ```powershell
   .\tests\runners\run_all_tests.ps1
   ```

2. **Check Results**
   ```powershell
   cat test_runs\TESTS_FINAL_REPORT.md
   ```

3. **View Detailed Results** (if needed)
   ```powershell
   cat test_runs\TEST_RUN_2026-06-07.md
   ```

4. **Address Failures** (if any)
   - Review recommendations in reports
   - Fix issues in code
   - Re-run tests to verify

---

## 📝 Test Run Date Format

All reports include:
```
TEST RUN DATE: 2026-06-07
Test Start Time: 08:31 UTC
Test End Time: 08:35 UTC
Total Duration: ~5 minutes
```

---

## 🎯 Test Success Metrics

✓ **Authentication**: Login, registration, validation, sessions - **All passing**  
✓ **Library**: Search, filtering, categories - **All passing**  
✓ **Posts**: Create, read, update, delete - **All passing**  
✓ **Insights**: Highlights, notes, management - **All passing**  
✓ **Import/Export**: JSON upload, backup - **All passing**  
✓ **Validation**: Error handling, edge cases - **All passing**  
⚠️ **Stats**: Dashboard page returns 500 (API works)  

---

## 🔄 User Flow Tests

User flow tests cover **complete end-to-end workflows**:

1. **Post Import Flow** - Import posts, categorize, manage
2. **Insights Creation** - Highlight text, create insights, add thoughts
3. **AI Analysis** - Configure API, run analysis, save feedback
4. **Multi-User Collab** - Create users, switch, verify isolation
5. **Post Organization** - Organize posts by metadata, search, filter
6. **AI Generation** - Generate posts in personal style, manage
7. **Export & Backup** - Export collections, backup, restore

**Run user flow tests**:
```powershell
python tests/runners/user_flow_tests.py
```

Or use the main runner which includes them.

## 💡 Tips

- **First run?** Use the runner script (auto-starts Flask)
- **Flask already running?** Use `-NoApp` flag:
  ```powershell
  .\run_all_tests.ps1 -NoApp
  ```
- **User flows only?** Run `python tests/runners/user_flow_tests.py`
- **Need help?** Check `tests/runners/README.md` for troubleshooting
- **Full test guide?** See `tests/functional/USER_FLOW_TEST_CASES.md`

---

## 🔗 Full Documentation

- Main test guide: `tests/README.md`
- Runner guide: `tests/runners/README.md`
- Results guide: `test_runs/README.md`
- Organization: `TEST_ORGANIZATION_SUMMARY.md`
- Test cases: `tests/functional/FUNCTIONAL_TEST_CASES.md`

---

## ✨ What's New

✓ Test scripts organized in `tests/runners/`  
✓ Results organized in `test_runs/`  
✓ All reports include test run dates  
✓ Convenient runner scripts (PowerShell & Batch)  
✓ Comprehensive documentation  
✓ Clear standards for future test runs  

---

**Status**: ✓ Ready to run  
**Last Tested**: 2026-06-07  
**Success Rate**: 98% (48/49)  

👉 **Next Step**: Run `tests/runners/run_all_tests.ps1` or `run_all_tests.bat`
