# Scrape Pipeline Automation — Design Spec

**Date:** 2026-04-29
**Repo:** chipotle-scrape-pipeline
**File to automate:** `scrape_pipeline.py`

---

## Overview

Automate the Firecrawl scrape pipeline using GitHub Actions so that `knowledge/raw/` is updated weekly without manual intervention. New markdown files are committed back to `main` automatically. Runs that produce no new content exit cleanly with no commit.

---

## Triggers

| Trigger | Details |
|---------|---------|
| `workflow_dispatch` | Manual run from GitHub Actions tab |
| `schedule` | `cron: '0 9 * * 1'` — every Monday at 9am UTC |

---

## Workflow File

**Path:** `.github/workflows/scrape-pipeline.yml`

---

## Permissions

```yaml
permissions:
  contents: write
```

Required so the commit-back step can push new files to `main`.

---

## Steps

1. **Checkout** — `actions/checkout@v4`
2. **Setup Python 3.11** — `actions/setup-python@v5`
3. **Install dependencies** — `pip install -r requirements.txt`
4. **Run scrape pipeline** — `python scrape_pipeline.py` with `FIRECRAWL_API_KEY` injected from repo secret. Non-zero exit fails the workflow.
5. **Commit & push new files** — shell block:
   - Check `git status --porcelain knowledge/raw/` for new files
   - If none: log "No new files, skipping commit" and exit 0
   - If any: configure git identity (`github-actions[bot]`), stage `knowledge/raw/`, commit as `chore: scrape pipeline run YYYY-MM-DD`, push to `main`

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| API failure (bad key, out of credits, network error) | Script exits non-zero → workflow step fails → run marked red → GitHub email notification |
| No new content (all results already exist) | Script exits 0 → commit step detects no changes → logs skip message → run marked green, no commit |

---

## Secrets Required

| Secret name | Where to add |
|-------------|-------------|
| `FIRECRAWL_API_KEY` | Repo → Settings → Secrets and variables → Actions → New repository secret |

`scrape_pipeline.py` already reads this via `os.getenv("FIRECRAWL_API_KEY")` — no code changes needed.

---

## Schedule Rationale

Weekly cadence (Monday 9am UTC) chosen because:
- Chipotle IR press releases are published a few times per month at most
- The script deduplicates by filename (date + URL slug), so more frequent runs rarely produce new files
- ~20 Firecrawl credits/month vs. ~150/month for daily
