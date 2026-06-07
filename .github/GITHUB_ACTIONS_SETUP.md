# GitHub Actions Setup Guide

**Setup Date**: 2026-06-07  
**Status**: Ready to use

---

## Overview

AttachmentLens now has automated CI/CD testing via GitHub Actions. Tests run automatically on every push and pull request.

---

## Workflow

### Single Optimized Workflow (`tests-linux.yml`)
- **Runs on**: `ubuntu-latest` (Linux)
- **When**: Every push to main/develop, PRs, daily at 2 AM UTC
- **Cost**: FREE for public repos
- **Speed**: ~2-3 minutes
- **Coverage**: All 74 tests (comprehensive, extended, user flows)
- **Use case**: Full CI/CD automation, PR feedback

This is the only workflow needed for fast, cost-effective continuous integration.

---

## What Gets Tested

### Automatic Testing
Every workflow runs:
- **Comprehensive Tests**: 22 functional tests (95% pass rate)
- **Extended Tests**: 27 extended tests (100% pass rate)
- **User Flow Tests**: 25 user flow scenarios (92% pass rate)

**Total**: 74 tests covering all major features

### On Pull Requests
- Tests run automatically
- Results posted as PR comment
- Reports available as artifacts
- Blocks merge if critical tests fail (optional)

---

## How to Use

### For Developers

#### View Test Results
1. Go to your PR
2. Scroll to "Checks" section
3. Click on test workflow
4. View real-time progress

#### Download Test Reports
1. Click "Actions" tab
2. Click the workflow run
3. Download "test-reports" artifact
4. Extract to see detailed results

### For Repository Admins

#### Enable/Disable Workflows
1. Go to "Actions" tab
2. Select workflow
3. Click "..." menu
4. Choose "Enable" or "Disable"

#### Modify Triggers
Edit `.github/workflows/tests.yml` or `tests-linux.yml`:

```yaml
on:
  push:
    branches: [ main, develop ]  # Which branches
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

#### Configure Concurrency

```yaml
concurrency:
  group: ${{ github.ref }}
  cancel-in-progress: true
```

This cancels old runs when new code is pushed.

---

## Workflow Details

### Windows Workflow (`tests.yml`)

#### Steps
1. **Checkout code** - Clones repository
2. **Setup Python** - Installs Python 3.12
3. **Install dependencies** - Installs Flask, requests
4. **Start Flask app** - Launches development server
5. **Wait for Flask** - Verifies app is ready
6. **Run tests** - Executes all three test suites
7. **Generate summary** - Creates test summary
8. **Upload artifacts** - Saves reports
9. **Comment PR** - Posts results to PR

#### Timing
- Total: ~3-5 minutes
- Depends on GitHub's queue

### Linux Workflow (`tests-linux.yml`)

Same as Windows but:
- Runs on Linux (faster startup)
- Uses bash scripts instead of PowerShell
- More cost-effective
- Better for CI/CD gates

---

## Test Report in PR

When tests complete, you'll see a comment like:

```
## 🧪 Test Results

Overall Results: 71/74 tests passed (96%)

✅ All tests passed!

📊 View detailed reports →
```

Click the link to see:
- Full test breakdown
- Pass/fail status by category
- Performance metrics
- Known issues

---

## Artifacts

### What's Saved
- `TEST_RUN_2026-06-07.md` - Detailed results
- `TESTS_FINAL_REPORT.md` - Final summary
- `TEST_EXECUTION_SUMMARY.md` - Executive summary

### Retention
- Kept for 30 days
- Configurable in workflow YAML
- Can be manually deleted

### Access
1. Actions tab → Workflow run → Artifacts
2. Download as ZIP
3. Extract to view reports

---

## Environment Variables (Optional)

Add secrets for external integrations:

1. Go to Settings → Secrets and variables → Actions
2. Create new repository secrets:
   - `ANTHROPIC_API_KEY` - For AI features
   - `GITHUB_TOKEN` - For GitHub integration (auto-set)

Then reference in workflow:

```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Customization

### Change Python Version

Edit `.github/workflows/tests.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']  # Test multiple versions
```

### Change Test Schedule

```yaml
schedule:
  - cron: '0 * * * *'  # Every hour
  - cron: '0 0 * * *'  # Daily at midnight
```

### Skip Tests for Certain Commits

In commit message, include:

```
[skip ci]
or
[ci skip]
```

---

## Troubleshooting

### Tests Fail in CI but Pass Locally

**Common causes**:
1. Missing environment variables
2. Different Python version
3. Port 5000 already in use
4. Dependencies not installed

**Solution**:
- Check workflow logs (click "Re-run" to debug)
- Verify Python version matches locally
- Check environment variables

### Workflow Doesn't Run

**Causes**:
1. Workflow is disabled
2. Wrong branch name in `on:`
3. Syntax error in YAML

**Solution**:
- Enable workflow in Actions tab
- Check branch names
- Validate YAML syntax

### Artifacts Not Uploading

**Cause**: Tests crashed before upload

**Solution**:
- Check test step logs
- Use `if: always()` to force uploads

---

## Best Practices

### 1. Run Tests Locally First
```cmd
tests\runners\QUICK_TEST.bat
```

### 2. Check Workflow Status
Always check the Actions tab before committing critical code.

### 3. Review Test Reports
Don't ignore test failures. Investigate and fix.

### 4. Keep Tests Fast
If CI takes too long:
- Run only critical tests on every push
- Run full suite on schedule

### 5. Monitor Flaky Tests
If tests pass/fail randomly:
- Investigate root cause
- Add timeouts
- Fix timing issues

---

## GitHub Pages Integration (Optional)

You can host test reports on GitHub Pages:

1. Enable Pages in Settings
2. Set source to "GitHub Actions"
3. Reports auto-deploy

Then access at: `https://username.github.io/AttachmentLens/test-reports/`

---

## Cost Considerations

### Windows Runners
- **Cost**: 1 minute = 2 Windows minutes (quota-aware)
- **Duration**: ~3-5 minutes per run
- **Estimate**: ~6-10 minutes quota per run

### Linux Runners
- **Cost**: Free (included in public repos)
- **Duration**: ~2-3 minutes per run
- **Estimate**: No quota cost

### Recommendation
- Use Linux for every-push testing
- Use Windows for release/main branch
- Use schedule for full daily testing

---

## Manual Trigger

To run tests manually without push:

1. Go to "Actions" tab
2. Select workflow
3. Click "Run workflow" button
4. Choose branch
5. Click "Run"

---

## PR Status Checks

### Require Checks Before Merge (Optional)

1. Settings → Branch protection rules
2. Create rule for `main`
3. Require status checks to pass
4. Select test workflows

Then PRs can't merge until tests pass.

---

## Example: Full Setup

### Step 1: Commit Workflows
```bash
git add .github/workflows/
git commit -m "Add GitHub Actions CI/CD"
git push origin main
```

### Step 2: View in Actions Tab
- Go to GitHub repo
- Click "Actions" tab
- See workflows running

### Step 3: Check PR Results
- Create a test PR
- See tests run automatically
- View results in PR checks

### Step 4: Monitor Dashboard
- Click workflow name
- View all runs
- Check success/failure trends

---

## Next Steps

1. ✅ Workflows are ready to use
2. Push code to trigger testing
3. Monitor Actions tab
4. Customize as needed

---

## Support

For issues:
1. Check workflow logs (Actions tab)
2. Review this guide
3. Check GitHub Actions documentation: https://docs.github.com/en/actions

---

**Status**: Ready to use  
**Workflows**: 2 (Windows + Linux)  
**Tests**: 74 total  
**Estimate**: 2-5 minutes per run
