# Phase 2 Next Steps - Action Plan

**Current Date:** February 21, 2026
**Status:** Framework complete, ready for testing phase

---

## 🎯 Immediate Next Steps (Priority Order)

### STEP 1: Fix Authentication Issue (Today/Tomorrow)
**Goal:** Get HTML download working
**Issue:** Authentication failed in download script
**Action:**
```bash
# Test authentication with a single projekt
python src/phase2/scraper.py

# If this fails, debug auth.py
# - Check if credentials in .env are correct
# - Verify login URL hasn't changed
# - Check browser console in Iris login page
```

**Expected Output:** Browser opens, logs in, navigates to project

---

### STEP 2: Test Single Project (Tomorrow)
**Goal:** Validate extractors work on real HTML
**Action:**
```bash
# Use the scraper on project 235 (known to exist)
/Users/enriquecarbonell/repo/irisbot/.venv/bin/python -c "
import asyncio
import sys
sys.path.insert(0, 'src')
from phase2.scraper import scrape_single_project

result = asyncio.run(scrape_single_project(235))
print(f'Success: {result.get(\"success\")}')
print(f'Units found: {result.get(\"units\", {}).get(\"count\")}')
print(f'Assets found: {len(result.get(\"assets\", []))}')
"
```

**Expected Output:**
```
Success: True
Units found: 12-25
Assets found: 2-10
```

**If fails:** Check what's in phase2_extractions/project_235_extraction.json

---

### STEP 3: Analyze Extraction Results
**Goal:** Understand what was extracted vs what should have been
**Action:**
```bash
# View extraction output
cat phase2_extractions/project_235_extraction.json | python -m json.tool

# Compare with actual page
# Visit: https://iris.infocasas.com.uy/proyecto/235
# Open DevTools (F12)
# Check what selectors found
```

**Debug Checklist:**
- [ ] Did `metadata` extract title? If not, fix h1 selector
- [ ] Did `units` find table? If not, try other table selectors
- [ ] Did `developer` open modal? If not, check button text
- [ ] Did `assets` find downloads? If not, check link patterns

---

### STEP 4: Fix Selectors Based on Real Data
**Goal:** Update CSS selectors to match actual HTML
**Action:**
```bash
# For each failing selector:
# 1. Open DevTools on https://iris.infocasas.com.uy/proyecto/235
# 2. Inspect the element you want
# 3. Try selectors manually in console:
#    document.querySelector("h1")
#    document.querySelector("h1.project-title")
#    document.querySelector("[class*='title']")
# 4. Update the selector in the extractor
```

**File to Edit:** `src/phase2/metadata_extractor.py` (and others)

**Example Fix:**
```python
# BEFORE (not working)
selector = "h1"

# AFTER (working)
selector = "h1.project-name, .project-header h1"
```

---

### STEP 5: Run on 10 Projects
**Goal:** Validate extractors work across different projects
**Action:**
```bash
# Create a test script
cat > test_10_projects.py << 'EOF'
import asyncio
import sqlite3
from src.phase2.scraper import scrape_multiple_projects

conn = sqlite3.connect('catalog_projects.db')
c = conn.cursor()
c.execute('SELECT project_id FROM projects ORDER BY RANDOM() LIMIT 10')
ids = [row[0] for row in c.fetchall()]
conn.close()

print(f"Testing {len(ids)} projects: {ids}")
results = asyncio.run(scrape_multiple_projects(ids, limit_per_run=10))
print(f"✓ {results['successful']} successful, ✗ {results['failed']} failed")
EOF

# Run it
/Users/enriquecarbonell/repo/irisbot/.venv/bin/python test_10_projects.py
```

**Success Criteria:**
- ✅ 8+/10 projects successful (80%+)
- ✅ Units extracted for all with units tables
- ✅ No unhandled exceptions
- ✅ Database saved for all

---

### STEP 6: Analyze Failure Patterns
**Goal:** Understand why some extractions fail
**Action:**
```bash
# Check failed projects
grep "success.*false" phase2_extractions/*.json | wc -l

# View specific failure
grep -l "success.*false" phase2_extractions/*.json | head -1 | xargs cat

# Common issues:
# - No units table on page (special projects)
# - Different HTML structure (variation)
# - Modal not opening (timing issue)
# - Missing assets (normal)
```

**Fix Strategy:**
```python
# If pattern found (e.g., 20% fail on same selector):
# Option 1: Add more selector variants
# Option 2: Use XPath instead of CSS
# Option 3: Use page.evaluate() for complex queries
```

---

### STEP 7: Implement Batch Processor
**Goal:** Process all 129 projects with progress tracking
**Action:**
```bash
# Create batch_scraper.py with:
# - Progress bar (tqdm)
# - Retry logic (3 attempts)
# - Rate limiting (2 sec between requests)
# - Error logging (to CSV)
# - Resume capability

# Run batch scraper
/Users/enriquecarbonell/repo/irisbot/.venv/bin/python batch_scraper.py --limit 50 --resume
```

**Expected Output:**
```
Phase 2 Batch Scraper
════════════════════════════════════════════════════════════
Processing 129 projects...

[████████████████████ 30%] 38/129 projects
├─ Successful: 35 ✅
├─ Failed: 2 ✗ (retrying...)
├─ Avg time: 3.2s/project
└─ ETA: 15 minutes

[Complete]
✓ 126/129 successful (97.7%)
✗ 3 failed (saved to failed_projects.csv)
```

---

## 📅 Timeline Estimate

| Task | Time | Status |
|------|------|--------|
| Fix auth issue | 30 min | 🔴 TODO |
| Test 1 project | 15 min | 🔴 TODO |
| Analyze results | 30 min | 🔴 TODO |
| Fix selectors | 1-2 hrs | 🔴 TODO |
| Test 10 projects | 1 hr | 🔴 TODO |
| Analyze failures | 30 min | 🔴 TODO |
| Batch processor | 2 hrs | 🔴 TODO |
| **Total** | **6-8 hrs** | 🔴 TODO |

---

## 🛠️ Tools & Commands Reference

### Database Queries
```bash
# Count records in each Phase 2 table
sqlite3 catalog_projects.db << EOF
SELECT
  'projects' as table_name, COUNT(*) as count FROM projects
UNION ALL
SELECT 'units', COUNT(*) FROM units
UNION ALL
SELECT 'developer_info', COUNT(*) FROM developer_info
UNION ALL
SELECT 'developer_assets', COUNT(*) FROM developer_assets;
EOF

# View sample scraped project
sqlite3 catalog_projects.db "SELECT project_id, description, phase2_scraped_at FROM projects WHERE phase2_scraped_at IS NOT NULL LIMIT 1;"

# Count units per project
sqlite3 catalog_projects.db "SELECT project_id, COUNT(*) as unit_count FROM units GROUP BY project_id ORDER BY unit_count DESC LIMIT 10;"
```

### Debugging
```bash
# Enable debug logging
LOG_LEVEL=DEBUG /Users/enriquecarbonell/repo/irisbot/.venv/bin/python src/phase2/scraper.py

# View extraction errors
grep -i "error\|exception" phase2_extractions/*.json | head -10

# Compare two projects
diff <(jq .metadata phase2_extractions/project_235.json) \
      <(jq .metadata phase2_extractions/project_236.json)
```

### File Locations
```
Working Directory: /Users/enriquecarbonell/repo/irisbot/

Key Files:
├── src/phase2/                  (Extractors)
│   ├── scraper.py               (Main orchestrator)
│   ├── metadata_extractor.py    (To fix if metadata fails)
│   ├── units_extractor.py       (To fix if units fail)
│   ├── developer_extractor.py   (To fix if developer fails)
│   └── assets_extractor.py      (To fix if assets fail)
├── phase2_extractions/          (JSON output)
│   └── project_XXX_extraction.json
├── catalog_projects.db          (Database)
└── tests/test_phase2_extractors.py (Tests)
```

---

## 🔍 Troubleshooting Guide

### Problem: "No units table found"
**Likely Cause:** CSS selector doesn't match this project's HTML
**Solution:**
1. Open DevTools on project page
2. Search for `<table>` in Elements
3. Try these selectors in console:
   ```js
   document.querySelector("table")
   document.querySelector("div[role='table']")
   document.querySelector("[class*='unit']")
   // etc.
   ```
4. Add working selector to units_extractor.py line ~60

### Problem: "Authentication failed"
**Likely Cause:** Credentials wrong or login flow changed
**Solution:**
1. Check .env has correct IRIS_EMAIL and IRIS_PASSWORD
2. Try manual login at https://iris.infocasas.com.uy
3. If login page changed, update auth.py selectors
4. Test with: `python src/auth.py` (if it has a test mode)

### Problem: "Modal not opening"
**Likely Cause:** Button text or timing issue
**Solution:**
1. Check actual button text on project page
2. Increase timeout: `await self.page.wait_for_selector(..., timeout=5000)`
3. Or disable modal extraction: `dev_ext_ractor = None`

---

## ✅ Validation Checklist

Before moving to batch processing, verify:

- [ ] Authentication works (can login and navigate)
- [ ] Metadata extractor works on test project
- [ ] Units table parser works (extracts >0 units)
- [ ] Developer extractor attempts modal (even if fails)
- [ ] Assets extractor finds download links
- [ ] JSON export works (valid JSON created)
- [ ] Database persistence works (data in DB)
- [ ] No unhandled exceptions in logs
- [ ] Performance acceptable (< 5 sec per project)
- [ ] Error messages are helpful

---

## 📊 Success Criteria (For Completion)

### Single Project Test
- ✅ All extractors return data (non-empty)
- ✅ JSON file created and valid
- ✅ Data inserted in database
- ✅ No exceptions in logs

### 10 Project Test
- ✅ 8+/10 projects successful (80%+)
- ✅ Units table found for projects with units
- ✅ Developer info attempted
- ✅ Avg time 2-5 sec per project

### Batch Processing
- ✅ All 129 projects attempted
- ✅ 90%+ success rate
- ✅ 1000+ units extracted
- ✅ 100+ developer records created
- ✅ Failed projects logged for review

---

## 🎯 If Stuck

### For CSS Selector Issues
1. Use DevTools to inspect actual element
2. Try multiple selector variations
3. As last resort, use page.evaluate() with custom JS
4. Document the variation for future projects

### For Timing Issues
1. Increase timeouts (generous is better than fast)
2. Add more wait_for_selector calls
3. Add intermediate sleep(1) between steps

### For Data Issues
1. Check what's actually on the page (manual inspection)
2. Print raw extracted data for debugging
3. Compare extraction logs with expected
4. Create a minimal reproducible example

### For Database Issues
1. Verify schema with: `sqlite3 catalog_projects.db ".schema units"`
2. Check for constraint violations in logs
3. Test INSERT manually before batch
4. Backup database before large batch runs

---

## 📝 Session Notes

### From Today's Session
```
✓ Framework complete: 3,825 lines of code
✓ Database extended: 5 new tables
✓ Extractors implemented: 5 modules
✓ Tests created: 19 passing
✓ Documentation: 730+ lines

⏳ Next: Real-world validation and refinement
```

### Known Issues to Track
1. Authentication timeout in HTML downloader (needs debug)
2. CSS selectors may need adjustment per project
3. Modal timing may be unpredictable
4. Error handling needs real-world testing

### Design Principles Implemented
- Modular (each extractor independent)
- Resilient (fallbacks for each failure mode)
- Testable (unit tests without browser)
- Documented (730+ lines)
- Extensible (easy to add new extractors)

---

**Document Version:** 1.0
**Last Updated:** Feb 21, 2026
**Next Review:** After first batch test run

**Next Session Goal:** Complete with 90%+ success rate on real projects
