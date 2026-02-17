# Pre-commit Hooks Setup Guide

**Purpose:** Automate code quality checks and enforce project standards before each commit.

---

## 🚀 Quick Setup

```bash
# 1. Install development dependencies
make install-dev

# 2. Install pre-commit hooks
make pre-commit-install

# 3. Verify hooks are installed
git hooks

# Done! Hooks will run automatically on every commit
```

⚠️ **IMPORTANT:** Pre-commit hooks require the `.venv` virtual environment to be activated. This happens automatically when:
- Using `make pre-commit-*` commands (they activate venv automatically)
- Committing via git (the git hook wrapper activates venv)
- Running hooks manually (activate venv first: `source .venv/bin/activate`)

---

## 📋 What Gets Checked

Pre-commit automatically validates every commit against the [Code Review Checklist](./CODING_STANDARDS.md#code-review-checklist):

### ✅ Code Quality (Automatic Fixes)
- **Black** - Code formatting (PEP 8)
- **isort** - Import organization
- **Trailing whitespace** - Cleanup
- **End-of-file fixer** - Proper line endings

### ⚠️ Code Quality (Must Fix Manually)
- **Flake8** - Style guide compliance
- **Pylint** - Advanced code analysis
- **pydocstyle** - Docstring conventions
- **mypy** - Type hint validation

### 🔒 Project Constraints
- **No Selenium** - Use Playwright only
- **No requests** - Use aiohttp only
- **No hardcoded paths** - Use pathlib
- **No credentials** - Use environment variables
- **No print()** - Use logging instead
- **Docstrings** - All public functions must have them
- **No merge conflicts** - Check for markers

### 🧪 Testing
- **pytest** - All tests must pass (collection check)
- **Coverage** - Maintained at 90%+ (run separately)

---

## 🔧 Using Pre-commit

### Automatic On Commit
Pre-commit runs automatically when you commit:

```bash
git add your_file.py
git commit -m "Add feature"
# Pre-commit hooks run here...
```

### Run Manually On All Files
```bash
# Check all files without committing
make pre-commit-run

# Or directly:
pre-commit run --all-files
```

### Run On Specific Files
```bash
pre-commit run --files path/to/file.py
```

### Skip Pre-commit (Not Recommended)
```bash
# If absolutely necessary
git commit --no-verify
```

### Update Hooks to Latest Versions
```bash
make pre-commit-update

# Or directly:
pre-commit autoupdate
```

---

## 📊 Hook Details

### 1. Black (Code Formatter)
**What:** Automatically formats Python code to PEP 8  
**Action:** Auto-fixes most issues  
**Config:** `--line-length=100` (matches CODING_STANDARDS.md soft limit)

```bash
# View changes before committing
git diff
```

### 2. isort (Import Organization)
**What:** Sorts and organizes imports  
**Action:** Auto-fixes  
**Config:** Uses black-compatible profile

```python
# Before
import requests
from pathlib import Path
import asyncio
from auth import authenticate

# After (auto-fixed)
import asyncio
from pathlib import Path

from auth import authenticate
```

### 3. Flake8 (PEP 8 Linter)
**What:** Checks Python style and formatting
**Action:** Manual fix required  
**Config:** Ignores E203, W503 (compatible with black)

Example violations:
- Unused imports
- Undefined variables
- Line too long (>100 chars)
- Multiple statements on one line

### 4. Pylint (Code Analysis)
**What:** Advanced code quality checks  
**Action:** Manual fix required  
**Config:** Max line length 100, extended analysis

Example violations:
- Missing docstrings
- Too many arguments
- Duplicate code
- Unreachable code

### 5. pydocstyle (Docstring Validator)
**What:** Validates docstring formats  
**Action:** Manual fix required  
**Config:** Google-style docstrings

Example violations:
```python
# Bad ❌
def parse_price(price_text):
    # Just a comment, not a docstring
    pass

# Good ✅
def parse_price(price_text: str) -> float:
    """Parse price string to float.
    
    Args:
        price_text: Price string like "USD 120.000"
    
    Returns:
        Float value without currency symbols
    """
```

### 6. mypy (Type Checking)
**What:** Static type checking  
**Action:** Manual fix required (warnings only, doesn't fail commit)  
**Config:** Strict optional, ignore missing imports

Example warnings:
```python
# Warning ⚠️
def scrape(url):  # Missing type hints
    pass

# Good ✅
async def scrape(url: str) -> dict:
    pass
```

### 7. Project Constraints (Custom)
**What:** Irisbot-specific validation  
**Action:** Manual fix required  
**Checks:**
- No Selenium imports → Use Playwright
- No requests imports → Use aiohttp
- No hardcoded file paths → Use pathlib
- No hardcoded credentials → Use .env
- No print() statements → Use logging

### 8. Docstrings Check (Custom)
**What:** Validates public functions have docstrings  
**Action:** Manual fix required  
**Scope:** Only public functions (not starting with `_`)

### 9. Type Hints Check (Custom)
**What:** Validates type hints on public functions  
**Action:** Manual fix required (warnings only)  
**Scope:** Parameters and return types on public functions

### 10. pytest (Test Suite)
**What:** Verifies tests can be collected (doesn't run them)  
**Action:** Manual fix required  
**Note:** Run `make test` separately to actually run tests

---

## 🐛 Common Issues & Solutions

### Issue 1: Pre-commit hooks slow on first run
```bash
# First run must download all tools
# Subsequent runs are much faster (cached)
# Use --no-output to suppress verbose output
pre-commit run --all-files --show-diff-on-failure
```

### Issue 2: Black and Flake8 conflict
```bash
# Already handled in config (black-compatible flake8 settings)
# If still occurs:
make format  # Let black fix it
```

### Issue 3: mypy complains about imports
```bash
# mypy might not find all stubs
# Add to .mypy.ini or .pre-commit-config.yaml:
# --ignore-missing-imports
# (Already configured)
```

### Issue 4: Pre-commit won't run
```bash
# Reinstall hooks
make pre-commit-install

# Check hook installation
git config hooks.precommit.active true
```

### Issue 5: Need to skip for emergency fix
```bash
# Use only if critical:
git commit --no-verify

# Then immediately fix and recommit without skipping
```

---

## 📝 Configuration

### View Current Configuration
```bash
cat .pre-commit-config.yaml
```

### Customize Hook Behavior

Edit `.pre-commit-config.yaml` to:
- Add/remove hooks
- Modify arguments
- Change excluded files
- Skip specific hooks

Example: Increase line length to 120
```yaml
  - repo: https://github.com/PyCQA/flake8
    hooks:
      - id: flake8
        args:
          - --max-line-length=120  # Changed from 100
```

Then update:
```bash
make pre-commit-update
```

---

## 🔗 Integration with Workflow

### Local Development
1. Install pre-commit: `make pre-commit-install`
2. Develop normally
3. Pre-commit runs automatically on commit (same validation as CI)
4. If failures: Fix and retry commit

### GitHub Actions (CI Pipeline)
CI pipeline in `.github/workflows/ci.yml` runs:

**Code Quality Validation (Same as local):**
- Pre-commit hooks: `pre-commit run --all-files`
  - Formatting (Black, isort)
  - Linting (Flake8, Pylint)
  - Type checking (mypy)
  - Documentation (pydocstyle)
  - Project constraints validation
  - File integrity checks

**Testing & Coverage:**
- Unit tests: `pytest --cov`
- Coverage threshold: 90% minimum
- Runs on Python 3.10, 3.11, 3.12, 3.13

**Why pre-commit in CI?**
- ✅ Same validation as local development
- ✅ Catches issues that slipped through locally
- ✅ Ensures consistency across all commits
- ✅ Prevents accumulation of technical debt
- ✅ Developers see exact same errors locally and in CI

### Feature Branches

```bash
# Work on feature
git checkout -b feature/my-feature

# Commit (pre-commit validation runs locally)
git add .
git commit -m "Implement feature"  # Local pre-commit runs

# If issues: Fix and retry locally
# Push when all local checks pass
git push origin feature/my-feature

# CI runs same validation on remote repository
# If all pass → Ready to merge
```

### Common Scenarios

**Scenario 1: Local commit passes, CI fails**
- Unlikely but possible (different Python version behavior)
- Check CI logs for details
- Fix and push new commit

**Scenario 2: Issues with timeout/resources in CI**
- CI runs all Python versions (3.10-3.13) in parallel
- Some checks might be slightly slower
- If timeout occurred, extend in `.pre-commit-config.yaml`

**Scenario 3: Need to update pre-commit hooks**
```bash
# Local
make pre-commit-update
git add .pre-commit-config.yaml
git commit -m "chore: update pre-commit hooks"

# CI will use updated config automatically
```

---

## ✅ Pre-commit Checklist

Before committing code:

- [ ] Development dependencies installed: `make install-dev`
- [ ] Pre-commit hooks installed: `make pre-commit-install`
- [ ] Code follows PEP 8 (Black will auto-fix)
- [ ] Imports organized (isort will auto-fix)
- [ ] All functions have docstrings (pydocstyle check)
- [ ] Public functions have type hints (mypy warning check)
- [ ] No Selenium, requests, print(), hardcoded paths
- [ ] Tests pass: `make test`
- [ ] Coverage maintained: `make coverage-check`

---

## 📚 Related Documentation

- [CODING_STANDARDS.md](./CODING_STANDARDS.md) - Code standards enforced by pre-commit
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Testing standards
- [AI_AGENT_GUIDELINES.md](./AI_AGENT_GUIDELINES.md) - For AI code generation

---

## 🔗 External Resources

- [pre-commit documentation](https://pre-commit.com)
- [Black code formatter](https://black.readthedocs.io)
- [isort import sorting](https://pycqa.github.io/isort)
- [Flake8 style guide](https://flake8.pycqa.org)
- [mypy type checking](https://mypy.readthedocs.io)

---

**Last updated:** February 16, 2026  
**Status:** Active
