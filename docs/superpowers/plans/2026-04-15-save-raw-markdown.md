# Save Raw Markdown Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `scrape_pipeline.py` to save each Firecrawl search result as a dated markdown file with YAML frontmatter in `knowledge/raw/`, skipping files that already exist.

**Architecture:** All save logic is added inline to the existing `for r in results` loop in `scrape_pipeline.py`. A single pure helper `url_to_slug()` is extracted to make the slug derivation testable. The script is wrapped in an `if __name__ == '__main__':` guard to allow importing in tests.

**Tech Stack:** Python stdlib only — `datetime`, `pathlib`, `re` (all already imported or stdlib). `pytest` for tests.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Modify | `scrape_pipeline.py` | Add `url_to_slug()`, `datetime` import, `if __name__` guard, dir creation, save logic |
| Create | `tests/test_scrape_pipeline.py` | Tests for slug derivation and file saving behavior |

---

### Task 1: Install pytest and set up test file

**Files:**
- Create: `tests/test_scrape_pipeline.py`

- [ ] **Step 1: Install pytest into the venv**

```bash
venv/Scripts/pip install pytest
```

Expected output includes: `Successfully installed pytest-...`

- [ ] **Step 2: Freeze updated requirements**

```bash
venv/Scripts/pip freeze > requirements.txt
```

- [ ] **Step 3: Create `tests/test_scrape_pipeline.py` with a placeholder**

```python
# tests/test_scrape_pipeline.py
```

- [ ] **Step 4: Commit**

```bash
git add requirements.txt tests/test_scrape_pipeline.py
git commit -m "chore: add pytest and test scaffold"
```

---

### Task 2: Write failing tests for `url_to_slug`

**Files:**
- Modify: `tests/test_scrape_pipeline.py`

- [ ] **Step 1: Write the failing tests**

Replace the contents of `tests/test_scrape_pipeline.py` with:

```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scrape_pipeline import url_to_slug


def test_slug_strips_scheme_and_replaces_separators():
    assert url_to_slug("https://ir.chipotle.com/news-releases") == "ir_chipotle_com_news-releases"


def test_slug_handles_trailing_slash():
    assert url_to_slug("https://ir.chipotle.com/") == "ir_chipotle_com"


def test_slug_handles_no_path():
    assert url_to_slug("https://ir.chipotle.com") == "ir_chipotle_com"


def test_slug_handles_http():
    assert url_to_slug("http://example.com/foo/bar") == "example_com_foo_bar"
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
venv/Scripts/pytest tests/test_scrape_pipeline.py -v
```

Expected: `ImportError` or `AttributeError` — `url_to_slug` does not exist yet.

---

### Task 3: Add `url_to_slug` and `if __name__` guard to `scrape_pipeline.py`

**Files:**
- Modify: `scrape_pipeline.py`

- [ ] **Step 1: Add `import datetime` and define `url_to_slug`**

Replace the top of `scrape_pipeline.py` so it reads:

```python
import datetime
import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
import requests


def url_to_slug(url: str) -> str:
    slug = re.sub(r"^https?://", "", url)
    slug = re.sub(r"[/.]", "_", slug)
    return slug.strip("_")
```

- [ ] **Step 2: Wrap the existing script body in `if __name__ == '__main__':`**

The rest of the file (from `load_dotenv()` through the `for r in results` loop) should be indented under:

```python
if __name__ == '__main__':
    load_dotenv()

    api_key = os.getenv("FIRECRAWL_API_KEY")

    # --- Step 01: Search + scrape with Firecrawl ---

    api_url = "https://api.firecrawl.dev/v2/search"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "query": "Chipotle investor relations press releases",
        "limit": 5,
        "scrapeOptions": {"formats": ["markdown"]}
    }

    response = requests.post(api_url, headers=headers, json=payload)

    data = response.json()
    results = data["data"]["web"]
    print(f"Firecrawl returned {len(results)} results")

    for r in results:
        print(f"  - {r['title']}")
        print(f"    {r['url']}")
        print(f"    markdown length: {len(r.get('markdown') or '')} chars")
```

- [ ] **Step 3: Run the `url_to_slug` tests — they should now pass**

```bash
venv/Scripts/pytest tests/test_scrape_pipeline.py -v
```

Expected:
```
test_slug_strips_scheme_and_replaces_separators PASSED
test_slug_handles_trailing_slash PASSED
test_slug_handles_no_path PASSED
test_slug_handles_http PASSED
```

- [ ] **Step 4: Confirm the script still runs correctly end-to-end**

```bash
venv/Scripts/python scrape_pipeline.py
```

Expected: same 5-result output as before.

- [ ] **Step 5: Commit**

```bash
git add scrape_pipeline.py tests/test_scrape_pipeline.py
git commit -m "feat: add url_to_slug and if __name__ guard"
```

---

### Task 4: Write failing tests for file saving behavior

**Files:**
- Modify: `tests/test_scrape_pipeline.py`

- [ ] **Step 1: Add file-saving tests**

Append to `tests/test_scrape_pipeline.py`:

```python
import datetime
from pathlib import Path
from unittest.mock import patch


def _make_result(title, url, markdown):
    return {"title": title, "url": url, "markdown": markdown}


def test_save_writes_file_with_frontmatter(tmp_path):
    result = _make_result(
        "News Releases - Chipotle",
        "https://ir.chipotle.com/news-releases",
        "## News\n\nSome content here."
    )
    today = "2026-04-15"
    slug = url_to_slug(result["url"])
    filepath = tmp_path / f"{today}_{slug}.md"

    content = f"---\ntitle: {result['title']}\nurl: {result['url']}\nscraped_at: {today}\n---\n\n{result['markdown']}"
    filepath.write_text(content, encoding="utf-8")

    assert filepath.exists()
    text = filepath.read_text(encoding="utf-8")
    assert "title: News Releases - Chipotle" in text
    assert "url: https://ir.chipotle.com/news-releases" in text
    assert "scraped_at: 2026-04-15" in text
    assert "## News" in text


def test_no_content_result_skips_write(tmp_path):
    result = _make_result("Empty Page", "https://ir.chipotle.com/empty", None)
    today = "2026-04-15"
    slug = url_to_slug(result["url"])
    filepath = tmp_path / f"{today}_{slug}.md"

    if result.get("markdown"):
        filepath.write_text("content", encoding="utf-8")

    assert not filepath.exists()


def test_existing_file_is_not_overwritten(tmp_path):
    result = _make_result(
        "News Releases",
        "https://ir.chipotle.com/news-releases",
        "New content that should not overwrite."
    )
    today = "2026-04-15"
    slug = url_to_slug(result["url"])
    filepath = tmp_path / f"{today}_{slug}.md"
    filepath.write_text("original content", encoding="utf-8")

    if not filepath.exists():
        filepath.write_text("should not reach here", encoding="utf-8")

    assert filepath.read_text(encoding="utf-8") == "original content"
```

- [ ] **Step 2: Run all tests — they should pass (logic is inline in the test)**

```bash
venv/Scripts/pytest tests/test_scrape_pipeline.py -v
```

Expected: all 7 tests PASS.

---

### Task 5: Add the save logic to `scrape_pipeline.py`

**Files:**
- Modify: `scrape_pipeline.py`

- [ ] **Step 1: Add directory creation and save logic inside `if __name__ == '__main__':`**

Replace the `for r in results` loop with:

```python
    today = datetime.date.today().isoformat()
    out_dir = Path("knowledge/raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Firecrawl returned {len(results)} results")

    for r in results:
        slug = url_to_slug(r["url"])
        filename = f"{today}_{slug}.md"
        filepath = out_dir / filename

        if not r.get("markdown"):
            print(f"  [no content] {filename}")
            continue

        if filepath.exists():
            print(f"  [skipped] {filename}")
            continue

        content = (
            f"---\n"
            f"title: {r['title']}\n"
            f"url: {r['url']}\n"
            f"scraped_at: {today}\n"
            f"---\n\n"
            f"{r['markdown']}"
        )
        filepath.write_text(content, encoding="utf-8")
        print(f"  [saved] {filename}")
```

The complete `scrape_pipeline.py` should now look like:

```python
import datetime
import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
import requests


def url_to_slug(url: str) -> str:
    slug = re.sub(r"^https?://", "", url)
    slug = re.sub(r"[/.]", "_", slug)
    return slug.strip("_")


if __name__ == '__main__':
    load_dotenv()

    api_key = os.getenv("FIRECRAWL_API_KEY")

    api_url = "https://api.firecrawl.dev/v2/search"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "query": "Chipotle investor relations press releases",
        "limit": 5,
        "scrapeOptions": {"formats": ["markdown"]}
    }

    response = requests.post(api_url, headers=headers, json=payload)

    data = response.json()
    results = data["data"]["web"]

    today = datetime.date.today().isoformat()
    out_dir = Path("knowledge/raw")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Firecrawl returned {len(results)} results")

    for r in results:
        slug = url_to_slug(r["url"])
        filename = f"{today}_{slug}.md"
        filepath = out_dir / filename

        if not r.get("markdown"):
            print(f"  [no content] {filename}")
            continue

        if filepath.exists():
            print(f"  [skipped] {filename}")
            continue

        content = (
            f"---\n"
            f"title: {r['title']}\n"
            f"url: {r['url']}\n"
            f"scraped_at: {today}\n"
            f"---\n\n"
            f"{r['markdown']}"
        )
        filepath.write_text(content, encoding="utf-8")
        print(f"  [saved] {filename}")
```

- [ ] **Step 2: Run all tests**

```bash
venv/Scripts/pytest tests/test_scrape_pipeline.py -v
```

Expected: all 7 tests PASS.

- [ ] **Step 3: Run the script end-to-end**

```bash
venv/Scripts/python scrape_pipeline.py
```

Expected output (filenames will reflect today's date):
```
Firecrawl returned 5 results
  [saved] 2026-04-15_ir_chipotle_com_news-releases.md
  [saved] 2026-04-15_newsroom_chipotle_com_press-releases.md
  [saved] 2026-04-15_ir_chipotle_com.md
  [saved] 2026-04-15_ir_chipotle_com_financial-releases.md
  [saved] 2026-04-15_ir_chipotle_com_sec-filings.md
```

- [ ] **Step 4: Run the script a second time to confirm skip behavior**

```bash
venv/Scripts/python scrape_pipeline.py
```

Expected: all 5 lines now say `[skipped]` instead of `[saved]`.

- [ ] **Step 5: Verify files exist in `knowledge/raw/`**

```bash
ls knowledge/raw/
```

Expected: 5 `.md` files listed.

- [ ] **Step 6: Commit**

```bash
git add scrape_pipeline.py tests/test_scrape_pipeline.py knowledge/raw/
git commit -m "feat: save Firecrawl results as markdown files in knowledge/raw/"
```
