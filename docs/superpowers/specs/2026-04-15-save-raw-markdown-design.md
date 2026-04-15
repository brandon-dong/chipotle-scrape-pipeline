# Design: Save Firecrawl Results as Markdown Files

**Date:** 2026-04-15
**Scope:** Extend `scrape_pipeline.py` to persist each Firecrawl search result as a markdown file in `knowledge/raw/`.

---

## Overview

After fetching search results from Firecrawl, the script iterates over each result and saves it as a markdown file with YAML frontmatter. Files are written inline in the existing `for r in results` loop — no new modules or helper functions.

---

## Directory

`knowledge/raw/` is created at runtime if it does not exist:

```python
Path("knowledge/raw").mkdir(parents=True, exist_ok=True)
```

---

## Filename Convention

```
knowledge/raw/YYYY-MM-DD_<url-slug>.md
```

- **Date:** the date the script runs (`datetime.date.today().isoformat()`)
- **URL slug:** derived from `r['url']` by stripping the scheme (`https://`, `http://`), then replacing every `/` and `.` with `_`, and stripping trailing underscores

Example: `https://ir.chipotle.com/news-releases` → `2026-04-15_ir_chipotle_com_news-releases.md`

---

## File Content

Each file contains YAML frontmatter followed by the raw markdown from Firecrawl:

```markdown
---
title: <r['title']>
url: <r['url']>
scraped_at: <YYYY-MM-DD>
---

<r['markdown']>
```

---

## Skip Logic

Before writing, the script checks three conditions in order:

1. **No content** — if `r['markdown']` is `None` or empty string, print `  [no content] <filename>` and skip
2. **File exists** — if the file already exists, print `  [skipped] <filename>` and skip
3. **Write** — otherwise write the file and print `  [saved] <filename>`

This makes the script safe to re-run: files already written for the current date are never overwritten.

---

## Console Output Example

```
Firecrawl returned 5 results
  [saved] 2026-04-15_ir_chipotle_com_news-releases.md
  [saved] 2026-04-15_newsroom_chipotle_com_press-releases.md
  [saved] 2026-04-15_ir_chipotle_com.md
  [saved] 2026-04-15_ir_chipotle_com_financial-releases.md
  [saved] 2026-04-15_ir_chipotle_com_sec-filings.md
```

---

## What Is Not Changing

- The Firecrawl API call, payload, and headers remain unchanged
- No new modules, helper functions, or classes are introduced
- `requirements.txt` does not change (`datetime` and `pathlib` are stdlib)
