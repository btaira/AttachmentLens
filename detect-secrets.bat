@echo off
REM -- Relaunch inside a persistent cmd window so it never closes on error --
if "%1"=="RUN" goto :main
start cmd /k "%~f0" RUN
exit

:main
cd /d "%~dp0"
echo.
echo ============================================================
echo   AttachmentLens -- Secret Detection Scan
echo   %DATE% %TIME%
echo ============================================================
echo.

REM ── Step 1: Python check ─────────────────────────────────────
echo Step 1 of 4: Checking for Python...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install from https://python.org
    goto :done
)
echo         OK - Python found.
echo.

REM ── Step 2: Install detect-secrets ───────────────────────────
echo Step 2 of 4: Checking for detect-secrets...
python -c "import detect_secrets" >nul 2>&1
if %errorlevel% equ 0 goto :ds_ok
echo         Installing detect-secrets (one-time)...
pip install detect-secrets -q
if %errorlevel% neq 0 (
    echo [ERROR] pip install failed. Run manually: pip install detect-secrets
    goto :done
)
echo         Installed.
goto :ds_done
:ds_ok
echo         OK - already installed.
:ds_done
echo.

REM ── Step 3: detect-secrets scan ──────────────────────────────
echo Step 3 of 4: Running detect-secrets deep scan...
python -m detect_secrets scan --exclude-files "data/.*" --exclude-files ".*\.db" --exclude-files ".*\.pyc" --exclude-files ".*\.bat" --exclude-files "docs/.*" > .secrets.new 2>&1
python detect-secrets-check.py
set DS_RESULT=%errorlevel%
if %DS_RESULT% equ 0 del /q .secrets.new 2>nul
echo.

REM ── Step 4: Grep for known patterns ──────────────────────────
echo Step 4 of 4: Checking for known API keys and tokens...
echo.
set FOUND=0

for /r . %%f in (*.py *.html *.js *.json *.yaml *.yml *.env *.txt) do (
    echo %%f | findstr /i "\\data\\ \\venv\\ \\__pycache__\\ \\.git\\ \\node_modules\\ \\docs\\" >nul
    if errorlevel 1 (
        findstr "sk-ant-api" "%%f" >nul 2>&1
        if not errorlevel 1 (
            echo   [HIT] Anthropic API key in: %%f
            echo         Action: Remove and rotate at console.anthropic.com
            echo.
            set FOUND=1
        )
        findstr "ghp_" "%%f" >nul 2>&1
        if not errorlevel 1 (
            echo   [HIT] GitHub token in: %%f
            echo         Action: Revoke at github.com/settings/tokens
            echo.
            set FOUND=1
        )
        findstr "github_pat_" "%%f" >nul 2>&1
        if not errorlevel 1 (
            echo   [HIT] GitHub fine-grained token in: %%f
            echo         Action: Revoke at github.com/settings/tokens
            echo.
            set FOUND=1
        )
    )
)
if %FOUND% equ 0 echo   [CLEAN] No known secret patterns found.
echo.

REM ── Summary ──────────────────────────────────────────────────
echo ============================================================
if %DS_RESULT% equ 0 (
    if %FOUND% equ 0 (
        echo   RESULT: ALL CLEAR - Safe to push to GitHub.
    ) else (
        echo   RESULT: REVIEW NEEDED - Fix [HIT] items above before pushing.
    )
) else (
    echo   RESULT: SECRETS DETECTED - Review [WARNING] items above.
    echo   Rotate any real credentials and remove from code.
)
echo ============================================================
echo.
echo Tip: Re-run this script after fixing to confirm clean.
echo      Type EXIT to close, or just leave this window open.
echo.

:done
cmd /k
