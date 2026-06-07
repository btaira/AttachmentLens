# Repository Folder Structure

**Updated**: 2026-06-07  
**Status**: ✓ Cleaned and organized

---

## 📁 Structure Overview

```
AttachmentLens/
│
├── 📄 README.md                      (Main project info)
├── 📄 QUICK_START_TESTS.md          (Quick test guide - READ THIS FIRST)
├── 📄 TODO.md                        (Project TODOs)
│
├── 📁 docs/                          (Documentation)
│   ├── DEPLOYMENT.md
│   ├── DOCKER.md
│   ├── GITHUB_PAGES.md
│   ├── ROADMAP_ENHANCED.md
│   ├── SETUP_SUMMARY.md
│   └── STRATEGIC_VISION.md
│
├── 📁 scripts/                       (Utility scripts)
│   ├── run.bat
│   ├── restart.bat
│   ├── push_to_github.bat
│   └── detect-secrets.bat
│
├── 📁 tests/                         (Test definitions & guides)
│   ├── README.md                     (Test framework overview)
│   ├── RUN_TESTS_GUIDE.md           (How to run from VS Code)
│   ├── TEST_RUNNER_OPTIONS.md       (Test runner options)
│   ├── TEST_ORGANIZATION_SUMMARY.md (Test architecture)
│   ├── USER_FLOWS_SUMMARY.md        (User flow reference)
│   ├── USER_FLOW_COMPLETION.md      (User flow completion report)
│   │
│   ├── 📁 functional/               (Test case definitions)
│   │   ├── FUNCTIONAL_TEST_CASES.md (49 functional tests)
│   │   ├── USER_FLOW_TEST_CASES.md  (70+ user flow scenarios)
│   │   └── TEST_RUN_TEMPLATE.md     (Test run template)
│   │
│   └── 📁 runners/                  (Test execution scripts)
│       ├── QUICK_TEST.bat           (⭐ Quick runner - use this)
│       ├── RUN_ALL_TESTS.bat        (Full runner with menu)
│       ├── RUN_TESTS.ps1            (PowerShell version)
│       ├── comprehensive_test.py    (22 functional tests)
│       ├── extended_tests.py        (27 extended tests)
│       ├── user_flow_tests.py       (70+ flow scenarios)
│       └── README.md                (Runner documentation)
│
├── 📁 test_runs/                     (Test results - git ignored)
│   ├── README.md                     (Test results guide)
│   ├── TESTS_FINAL_REPORT.md        (Final summary)
│   ├── TEST_RUN_COMPREHENSIVE_2026-06-07.md
│   ├── TEST_EXECUTION_SUMMARY.md
│   └── TEST_RUN_2026-06-07.md
│
├── 📁 templates/                     (Flask templates)
├── 📁 static/                        (Static files)
├── 📁 app.py                         (Main Flask app)
└── 📁 posts.db                       (Database)
```

---

## 🎯 Quick Navigation

### For Testing
```
→ Start here:    QUICK_START_TESTS.md
→ Run tests:     tests/runners/QUICK_TEST.bat
→ Full guide:    tests/RUN_TESTS_GUIDE.md
→ Test cases:    tests/functional/
→ Results:       test_runs/
```

### For Development
```
→ Project info:  README.md
→ App code:      app.py
→ Database:      posts.db
→ Web:           templates/ + static/
```

### For Documentation
```
→ Architecture:  tests/TEST_ORGANIZATION_SUMMARY.md
→ User flows:    tests/USER_FLOWS_SUMMARY.md
→ Deployment:    docs/DEPLOYMENT.md
→ Docker:        docs/DOCKER.md
```

### For Utilities
```
→ Run app:       scripts/run.bat
→ Restart:       scripts/restart.bat
→ Push code:     scripts/push_to_github.bat
→ Check secrets: scripts/detect-secrets.bat
```

---

## 📋 File Locations

### Root Level (3 files)
| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `QUICK_START_TESTS.md` | Quick test reference |
| `TODO.md` | Project TODOs |

### docs/ (6 files)
| File | Purpose |
|------|---------|
| `DEPLOYMENT.md` | Deployment guide |
| `DOCKER.md` | Docker instructions |
| `GITHUB_PAGES.md` | GitHub Pages setup |
| `ROADMAP_ENHANCED.md` | Project roadmap |
| `SETUP_SUMMARY.md` | Setup summary |
| `STRATEGIC_VISION.md` | Strategic vision |

### tests/ (6 files + 2 subfolders)
| File | Purpose |
|------|---------|
| `README.md` | Test framework overview |
| `RUN_TESTS_GUIDE.md` | How to run tests |
| `TEST_RUNNER_OPTIONS.md` | Test runner reference |
| `TEST_ORGANIZATION_SUMMARY.md` | Test architecture |
| `USER_FLOWS_SUMMARY.md` | User flow guide |
| `USER_FLOW_COMPLETION.md` | Completion report |

### tests/functional/ (3 files)
| File | Purpose |
|------|---------|
| `FUNCTIONAL_TEST_CASES.md` | 49 functional tests |
| `USER_FLOW_TEST_CASES.md` | 70+ flow scenarios |
| `TEST_RUN_TEMPLATE.md` | Test run template |

### tests/runners/ (7 files)
| File | Purpose |
|------|---------|
| `QUICK_TEST.bat` | ⭐ **Quick test runner** |
| `RUN_ALL_TESTS.bat` | Full test runner |
| `RUN_TESTS.ps1` | PowerShell runner |
| `comprehensive_test.py` | 22 functional tests |
| `extended_tests.py` | 27 extended tests |
| `user_flow_tests.py` | 70+ flow tests |
| `README.md` | Runner documentation |

### scripts/ (4 files)
| File | Purpose |
|------|---------|
| `run.bat` | Start Flask app |
| `restart.bat` | Restart Flask app |
| `push_to_github.bat` | Push code to GitHub |
| `detect-secrets.bat` | Check for secrets |

### test_runs/ (5 files)
| File | Purpose |
|------|---------|
| `README.md` | Results documentation |
| `TESTS_FINAL_REPORT.md` | Final test summary |
| `TEST_RUN_COMPREHENSIVE_2026-06-07.md` | Detailed results |
| `TEST_EXECUTION_SUMMARY.md` | Executive summary |
| `TEST_RUN_2026-06-07.md` | Original results |

---

## 🚀 How to Use

### Running Tests
```
From project root in VS Code terminal:

cd tests/runners
QUICK_TEST.bat
```

Or from any location:
```
tests\runners\QUICK_TEST.bat
```

### Viewing Test Results
```
test_runs\TESTS_FINAL_REPORT.md
```

### Reading Documentation
```
docs\DEPLOYMENT.md
tests\USER_FLOWS_SUMMARY.md
```

### Running Utilities
```
scripts\run.bat          (Start Flask)
scripts\push_to_github.bat (Push code)
```

---

## 📊 Organization Benefits

✓ **Cleaner Root** - Only essential files visible  
✓ **Better Organization** - Files grouped by purpose  
✓ **Easy Navigation** - Clear folder structure  
✓ **Maintainable** - Easy to find what you need  
✓ **Professional** - Industry-standard layout  

---

## 🎯 Getting Started

1. **First time?**
   - Read: `README.md`
   - Then: `QUICK_START_TESTS.md`

2. **Want to run tests?**
   - Open: `tests/runners/` folder
   - Run: `QUICK_TEST.bat`

3. **Need documentation?**
   - Explore: `docs/` folder
   - Or: Individual guide files

4. **Want to develop?**
   - Start: `app.py`
   - Use: `scripts/` utilities as needed

---

## 🔗 Cross-References

### Test Files Link To:
- `tests/README.md` → Overview
- `tests/RUN_TESTS_GUIDE.md` → VS Code instructions
- `tests/runners/` → Execution scripts
- `tests/functional/` → Test definitions

### Documentation Files Link To:
- `docs/DEPLOYMENT.md` → Deployment
- `docs/DOCKER.md` → Docker setup
- `tests/TEST_ORGANIZATION_SUMMARY.md` → Test architecture

### Quick Reference:
- `QUICK_START_TESTS.md` → Fast guide
- `tests/TEST_RUNNER_OPTIONS.md` → Test options
- `test_runs/` → Latest results

---

## 📦 Summary

**Root Level**: 3 essential files  
**Documentation**: 6 files in docs/  
**Tests**: 13 files organized in tests/  
**Results**: 5 files in test_runs/  
**Scripts**: 4 utility scripts  

**Total**: ~30 organized files  
**Total Before**: ~20 at root level  

**Result**: Much cleaner and more professional!

---

**Status**: ✓ Organized  
**Last Updated**: 2026-06-07  
**Recommendation**: Use `QUICK_START_TESTS.md` as your entry point
