# PDE ExamTopics Retarget Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Retarget ExamTopics tooling and the published study app from Professional Cloud Architect to Professional Data Engineer.

**Architecture:** Keep the crawl → optional discussion refresh → build-study-app pipeline. Change exam slug/URLs/defaults/branding to PDE. Builder includes all crawled PDE questions (no PCA case-study filter).

**Tech Stack:** Python 3, Playwright, BeautifulSoup, Requests, static GitHub Pages HTML/JSON

---

## File map

| File | Responsibility |
|---|---|
| `tools/gcp_cert/crawl_examtopics.py` | Playwright crawl of PDE exam pages |
| `tools/gcp_cert/fetch_pde_discussions.py` | Discussion refresh for PDE (replaces PCA fetcher) |
| `tools/gcp_cert/tests/test_fetch_pde_discussions.py` | Unit tests for PDE fetcher |
| `tools/gcp_cert/build_full_real_app.py` | Build root study app from PDE JSON |
| `tools/gcp_cert/README.md` | Tooling docs |
| `README.md` | Site docs |
| Root study assets | `index.html`, `full-real-study-data.json`, manifest, sw |

### Task 1: PDE discussion URL tests + fetcher

**Files:**
- Create: `tools/gcp_cert/fetch_pde_discussions.py`
- Create: `tools/gcp_cert/tests/test_fetch_pde_discussions.py`
- Delete: `tools/gcp_cert/fetch_pca_discussions.py`, `tools/gcp_cert/tests/test_fetch_pca_discussions.py`

- [ ] Write tests accepting `exam-professional-data-engineer` and rejecting other exams / PCA
- [ ] Implement fetcher retargeted from PCA script
- [ ] Run `python3 -m unittest discover -s tools/gcp_cert/tests -v`

### Task 2: Retarget crawler

**Files:**
- Modify: `tools/gcp_cert/crawl_examtopics.py`

- [ ] Set BASE_URL to professional-data-engineer
- [ ] Discussion URLs use exam-professional-data-engineer
- [ ] Defaults: `pde_questions_crawled.html`, `pde_crawl_checkpoint.json`
- [ ] Titles/branding → Professional Data Engineer

### Task 3: Retarget builder + site branding

**Files:**
- Modify: `tools/gcp_cert/build_full_real_app.py`
- Modify: `README.md`, `tools/gcp_cert/README.md`
- Modify: `manifest.webmanifest`, `sw.js`, `index.html` (via builder)

- [ ] SOURCE defaults to PDE crawl JSON in repo
- [ ] Include **all** source questions (drop PCA selected_keys / OLDER_CASE_KEYS filter)
- [ ] Remove PCA case-name constants; keep generic cue helpers where useful
- [ ] Brand outputs as GCP PDE / Professional Data Engineer
- [ ] Update READMEs

### Task 4: Crawl PDE + rebuild study app

- [ ] Install deps if needed (`playwright`, `beautifulsoup4`)
- [ ] Run crawler (visible browser; user solves CAPTCHA)
- [ ] Run builder against crawled JSON
- [ ] Verify question count ~349 and titles say Professional Data Engineer

### Task 5: Verify

- [ ] Unit tests pass
- [ ] Spot-check JSON for PDE discussion URLs
- [ ] Confirm README no longer presents PCA as the active cert
