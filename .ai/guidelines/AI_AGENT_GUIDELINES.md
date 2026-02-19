# AI Agent Execution Guidelines

**Purpose:** Minimal rules for AI agent code generation and cleanup. All other standards are in related documents.

---

## 📋 Quick Reference

| What | Rule | See Also |
|------|------|----------|
| **Code language** | 🇬🇧 **English only** | [CODING_STANDARDS.md](./CODING_STANDARDS.md) |
| **Documentation** | 🇬🇧 **English only** | [CODING_STANDARDS.md](./CODING_STANDARDS.md) |
| **Code location** | 📁 **`src/` directory only** | This document |
| **Tests location** | 🧪 **`tests/` directory only** | [TESTING_GUIDE.md](./TESTING_GUIDE.md) |
| **Documentation files** | 📝 **Update existing, don't create new** | This document |
| **Code style** | Follow project standards | [CODING_STANDARDS.md](./CODING_STANDARDS.md) |
| **Testing** | Maintain 90%+ coverage | [TESTING_GUIDE.md](./TESTING_GUIDE.md) |
| **Temp files** | 🗑️ **DELETE before finishing** | This document |

---

## 📂 Project Directory Structure Rule

**STRICT:** All AI-generated code must follow this directory structure:

### ✅ Application Code

**Location:** `src/` directory ONLY

```
src/
├── scrape_catalog_phase1.py    # Main scraper
├── auth.py                      # Authentication
├── config.py                    # Configuration
├── database.py                  # Database async utilities
├── db_manager.py                # DB manager class
├── downloader.py                # File download utilities
├── utils.py                     # Utility functions
└── iris_selectors.py            # CSS/XPath selectors
```

**Rule:**
- All `.py` application code → `src/`
- All application-level logic → `src/`
- Configuration, utilities, helpers → `src/`

### ✅ Test Code

**Location:** `tests/` directory ONLY

```
tests/
├── conftest.py                  # Pytest configuration & fixtures
├── test_auth.py                 # Auth tests
├── test_config.py               # Config tests
├── test_database.py             # Database tests
├── test_scrape_catalog.py       # Scraper tests
└── test_utils.py                # Utils tests
```

**Rule:**
- All `.py` test code → `tests/`
- All pytest configuration → `tests/conftest.py`
- All test fixtures → `tests/conftest.py`
- All test cases → `tests/test_*.py`

### ❌ NEVER Create

- Application code in `tests/`
- Test code outside `tests/`
- Individual test files at root level

---

## 📝 Documentation Update Rule

**CRITICAL:** Maintain single source of truth for all information.

### ✅ DO Update Existing Documentation

When implementing features or changes, update the relevant existing document:

| Change Type | Document to Update |
|-------------|-------------------|
| New code/function | [CODING_STANDARDS.md](./CODING_STANDARDS.md) |
| Database changes | `/.ai/context/DATA_MODEL.md` |
| Authentication changes | [SCRAPING_RULES.md](./SCRAPING_RULES.md) |
| Testing requirements | [TESTING_GUIDE.md](./TESTING_GUIDE.md) |
| Architecture changes | `/.ai/context/ARCHITECTURE.md` |
| Configuration additions | [CODING_STANDARDS.md](./CODING_STANDARDS.md) or `README.md` |

**Example:** Adding new config variable:
```python
# src/config.py
NEW_TIMEOUT_MS: Final[int] = int(os.getenv("NEW_TIMEOUT_MS", "5000"))
```
→ Update: `README.md` and/or `/.ai/context/ARCHITECTURE.md` with the new config

### ❌ NEVER Create New Documentation Files

**UNLESS explicitly requested in the prompt**, do NOT:
- Create `NEW_FEATURE.md` for new features → Update existing docs
- Create `CHANGE_LOG.md` for changes → Update existing docs
- Create `FEATURE_SUMMARY.md` → Update existing docs
- Create `CHANGE_DETAILS.md` → Update existing docs
- Create duplicate documentation of any kind

**Why:** Avoids documentation fragmentation and keeps information synchronized.

**Exception:** Only create new docs if prompt explicitly says "Create documentation for X" or "Create a guide for Y"

---

## 🎯 Temporary File Cleanup Rule

**Rule:** All temporary, intermediate, and analysis files created during prompt resolution must be deleted before marking the task complete.

### Temporary Files to DELETE

**Analysis/Debug scripts (always delete):**
- `*_ANALYSIS*.md`, `*_ANALYSIS*.py`
- `*_DEBUG*.py`, `*_SUMMARY*.md`, `*_SUMMARY*.json`
- `do_*.py` (one-off utility scripts)
- `analyze_*.py`, `debug_*.py`, `inspect_*.py`, `explore_*.py`, `find_*.py`

**Refactoring/Translation work (always delete):**
- `TRANS*.md`, `TRANS*.json`, `TRANS*.csv`
- `REFACTOR*.md`, `PLAN*.md`
- `*_IMPLEMENTATION_GUIDE*.md`, `*_NEEDS*.md`, `*_CHECKLIST*.csv`

### Files to KEEP

Only keep if they provide **ongoing value** to developers:
- `README.md` - Main project documentation
- `TESTING_QUICKSTART.md` - Quick reference
- `*_REPORT.md` - Final technical reports (if valuable for future reference)
- `*_COMPLETE.md` - Completion summaries (if they document major milestones)

---

## 🔄 Workflow

### Before Starting
1. Review context from `.ai/` directory (INDEX.md, CODING_STANDARDS.md, etc.)
2. All current standards apply to generated code

### During Execution
1. Create temporary files as needed for analysis/processing
2. Follow all standards in [CODING_STANDARDS.md](./CODING_STANDARDS.md)
3. Maintain test coverage ([TESTING_GUIDE.md](./TESTING_GUIDE.md))

### Before Finalizing ✅ CRITICAL

**Delete all temporary files:**
```bash
# List files to delete first
find . -name "TRANS*.md" -o -name "*_ANALYSIS*.py" -o -name "do_*.py"

# Delete if safe
rm -f TRANS*.md TRANS*.json do_*.py *_ANALYSIS*.*
```

**Verify cleanup:**
```bash
git status  # Should show only production files
```

### Completion Checklist

- [ ] Code produced
- [ ] All tests passing (83/83) ✅
- [ ] Documentation updated
- [ ] All temporary files DELETED ✅
- [ ] Ready for commit

---

## 🔐 Protected: Already Implemented Standards

These are already enforced by existing documentation - no duplication:

| Standard | Document | What It Covers |
|----------|----------|---|
| **Code Style** | [CODING_STANDARDS.md](./CODING_STANDARDS.md) | PEP 8, naming, imports, type hints, error handling, logging, security |
| **Testing** | [TESTING_GUIDE.md](./TESTING_GUIDE.md) | Test organization, fixtures, naming, assertions, coverage |
| **CI/CD** | [CI_CD_PIPELINE.md](./CI_CD_PIPELINE.md) | GitHub Actions, matrix testing, deployment |
| **Scraping** | [SCRAPING_RULES.md](./SCRAPING_RULES.md) | Selectors, rate limiting, error handling |
| **Architecture** | [../context/ARCHITECTURE.md](../context/ARCHITECTURE.md) | System design, components, data flow |
| **Data Model** | [../context/DATA_MODEL.md](../context/DATA_MODEL.md) | Database schema, relationships, queries |

**AI agents:** Generate code following these standards. They're comprehensive and don't need repetition here.

---

## 📝 Language Rule: English Only (with 1 Exception)

**Applied to:**
- All source code
- All comments and docstrings
- All documentation and error messages
- All logging output

**Exception:** Preserve Spanish-language content when it **matches website criteria** (e.g., CSS selectors for Spanish buttons, test strings validating website content).

See [CODING_STANDARDS.md - Security Best Practices](./CODING_STANDARDS.md#security) for more details.

---

## 🛠️ Integration with .gitignore

The following patterns are in `.gitignore` to prevent accidental commits of temporary files:

```gitignore
# AI Agent temporary files (MUST BE DELETED after task completion)
*_ANALYSIS*.md
*_ANALYSIS*.py
*_DEBUG*.py
*_SUMMARY*.md
*_SUMMARY*.json
do_*.py
analyze_*.py
debug_*.py
inspect_*.py
explore_*.py

# Translation/refactoring temporary files
TRANS*.md
TRANS*.json
TRANS*.csv
REFACTOR*.md
PLAN*.md
*_IMPLEMENTATION_GUIDE*.md
*_NEEDS*.md
*_CHECKLIST*.csv

# Build artifacts
*.tmp
.analysis/
.temp/
```

If a pattern matches your file but you think it should be committed, ask in code review instead of overriding .gitignore.

---

## ✅ Summary

| Item | Rule |
|------|------|
| **Code language** | English (follow [CODING_STANDARDS.md](./CODING_STANDARDS.md)) |
| **Temp files** | Delete before finalizing |
| **Testing** | Maintain coverage (see [TESTING_GUIDE.md](./TESTING_GUIDE.md)) |
| **Standards** | Follow [CODING_STANDARDS.md](./CODING_STANDARDS.md) |
| **Context available** | All .ai/ directory loaded during execution |

**Default:** All existing project standards apply. This document only adds the temporary file cleanup rule.

---

**Last updated:** February 16, 2026
**Status:** Active

For full standards reference, see [CODING_STANDARDS.md](./CODING_STANDARDS.md) and other documents in `.ai/guidelines/`
