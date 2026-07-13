# Separate PCA + PDE Pages Implementation Plan

> **For agentic workers:** Use executing-plans / implement task-by-task. Steps use checkbox syntax.

**Goal:** Restore PCA on `index.html` and publish PDE 2024–now on `pde.html`.

**Architecture:** Fix discussion-year parsing, refresh PDE JSON years, build a second study page from filtered PDE data while leaving PCA assets restored from git.

**Tech Stack:** Python 3, BeautifulSoup/Requests, static HTML/JSON

---

### Task 1: Year parsing (TDD)

- [ ] Add unit test for `parse_question_from_html` extracting year from `comment-date[title]`
- [ ] Implement year extraction in `fetch_pde_discussions.py`
- [ ] Run unit tests

### Task 2: Restore PCA + refresh PDE years

- [ ] `git checkout HEAD -- index.html full-real-study-data.json full-real-study-reference.md manifest.webmanifest sw.js`
- [ ] Refresh years on all rows in `pde_questions_crawled.json`
- [ ] Confirm 2024+ count > 0

### Task 3: PDE builder + page

- [ ] Update `build_full_real_app.py` (or PDE-specific path) to write `pde.html`, `pde-study-data.json`, `pde-study-reference.md` with `--min-year 2024`, leaving `index.html` alone
- [ ] Update README links
- [ ] Verify PCA index untouched and PDE page filters correctly
