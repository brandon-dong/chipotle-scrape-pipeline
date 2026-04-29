# Scrape Pipeline Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a GitHub Actions workflow that runs `scrape_pipeline.py` on a weekly schedule and commits any new `knowledge/raw/` files back to `main`.

**Architecture:** A single workflow YAML file with `workflow_dispatch` + weekly `schedule` triggers. After the script runs, a shell block checks `git status` to detect new files; if any exist it commits and pushes them, otherwise it exits cleanly with no commit. No changes to `scrape_pipeline.py` are needed — it already reads `FIRECRAWL_API_KEY` from the environment.

**Tech Stack:** GitHub Actions, Python 3.11, `actions/checkout@v4`, `actions/setup-python@v5`

---

## File Map

| Action | Path | Responsibility |
|--------|------|---------------|
| Create | `.github/workflows/scrape-pipeline.yml` | Full workflow definition |
| No change | `scrape_pipeline.py` | Already environment-ready |

---

### Task 1: Create the workflow file

**Files:**
- Create: `.github/workflows/scrape-pipeline.yml`

- [ ] **Step 1: Create the workflows directory**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Write the workflow file**

Create `.github/workflows/scrape-pipeline.yml` with this exact content:

```yaml
name: Scrape Pipeline

on:
  workflow_dispatch:
  schedule:
    - cron: '0 9 * * 1'

permissions:
  contents: write

jobs:
  scrape:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run scrape pipeline
        env:
          FIRECRAWL_API_KEY: ${{ secrets.FIRECRAWL_API_KEY }}
        run: python scrape_pipeline.py

      - name: Commit and push new files
        run: |
          if [ -n "$(git status --porcelain knowledge/raw/)" ]; then
            git config user.name "github-actions[bot]"
            git config user.email "github-actions[bot]@users.noreply.github.com"
            git add knowledge/raw/
            git commit -m "chore: scrape pipeline run $(date +%Y-%m-%d)"
            git push
          else
            echo "No new files, skipping commit"
          fi
```

- [ ] **Step 3: Commit the workflow file**

```bash
git add .github/workflows/scrape-pipeline.yml
git commit -m "feat: add GitHub Actions workflow for scrape pipeline"
```

- [ ] **Step 4: Push to GitHub**

```bash
git push
```

---

### Task 2: Add the secret to GitHub

**Files:** (no file changes — done in GitHub UI)

- [ ] **Step 1: Navigate to repo secrets**

Go to your `chipotle-scrape-pipeline` repo on GitHub →
**Settings** → **Secrets and variables** → **Actions** → **New repository secret**

- [ ] **Step 2: Add the secret**

- **Name:** `FIRECRAWL_API_KEY`
- **Secret:** your `fc-...` key from your local `.env` file

Click **Add secret**.

---

### Task 3: Verify the workflow runs correctly

**Files:** (no file changes — verification only)

- [ ] **Step 1: Trigger a manual run**

On GitHub → **Actions** tab → **Scrape Pipeline** → **Run workflow** → **Run workflow**.

- [ ] **Step 2: Confirm the run finishes green**

Wait for the run to complete (~30–60 seconds). Open the run log and verify:
- The "Run scrape pipeline" step shows lines like `[saved] 2026-...md` or `[skipped] ...` (not a stack trace)
- The "Commit and push new files" step shows either `[main ...]  chore: scrape pipeline run ...` or `No new files, skipping commit`

If the "Run scrape pipeline" step exits non-zero, check:
- `FIRECRAWL_API_KEY` secret name matches exactly (case-sensitive)
- The secret value doesn't have leading/trailing whitespace

- [ ] **Step 3: Verify the schedule appears on GitHub**

Go to **Actions** → **Scrape Pipeline**. The page should show "This workflow has a schedule." confirming the cron is registered.

---

### Task 4: Confirm commit-back works (optional smoke test)

> Skip this if Task 3's manual run already produced a commit. Only needed if the run showed "No new files, skipping commit" and you want to verify the commit path works.

**Files:** (no file changes)

- [ ] **Step 1: Temporarily modify the script query to force a new result**

In `scrape_pipeline.py`, change the query string temporarily:

```python
"query": "Chipotle investor relations press releases 2025",
```

- [ ] **Step 2: Commit and push the temporary change**

```bash
git add scrape_pipeline.py
git commit -m "test: force new scrape results for commit-back verification"
git push
```

- [ ] **Step 3: Trigger another manual run and confirm a commit appears**

On GitHub → **Actions** → **Scrape Pipeline** → **Run workflow**.
After the run, check the repo's commit history — you should see a new commit from `github-actions[bot]`.

- [ ] **Step 4: Revert the query change**

```python
"query": "Chipotle investor relations press releases",
```

```bash
git add scrape_pipeline.py
git commit -m "revert: restore original scrape query"
git push
```
