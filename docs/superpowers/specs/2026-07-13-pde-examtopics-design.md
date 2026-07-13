# Professional Data Engineer ExamTopics Retarget

**Date:** 2026-07-13  
**Status:** Approved design  
**Goal:** Replace PCA ExamTopics tooling and published study content with Google Professional Data Engineer (PDE).

## Context

This repository currently studies GCP Professional Cloud Architect (PCA):

- `tools/gcp_cert/crawl_examtopics.py` crawls PCA exam pages.
- `tools/gcp_cert/fetch_pca_discussions.py` refreshes PCA discussion pages.
- `tools/gcp_cert/build_full_real_app.py` builds the published PCA study app.
- Root `index.html`, `full-real-study-data.json`, and related PCA mindmap/keyword assets power GitHub Pages.

The user has finished PCA and wants the same workflow for Professional Data Engineer only — no dual-cert site.

ExamTopics PDE entry point:

- Exam pages: `https://www.examtopics.com/exams/google/professional-data-engineer/view/`
- Discussion slug: `exam-professional-data-engineer`
- Expected size: ~349 questions across ~35 pages (10 questions per page)

## Decision

**Retarget existing tools and replace the published app with PDE** (not keep PCA alongside PDE, and not leave scripts parameterized without updating the live study page).

## Architecture

```
ExamTopics PDE pages
        │
        ▼
crawl_examtopics.py  ──►  pde_questions_crawled.{json,html}
        │
        ▼ (optional later refresh)
fetch_pde_discussions.py  ──►  pde_questions_YYYY-MM-DD.{json,html}
        │
        ▼
build_full_real_app.py  ──►  index.html + full-real-study-data.json (+ reference md)
```

Same three-stage pipeline as PCA; only exam identity, defaults, labels, and published inputs change.

## Components

### 1. Crawler (`tools/gcp_cert/crawl_examtopics.py`)

- Change `BASE_URL` to the PDE `/view/` path.
- Build discussion URLs with `exam-professional-data-engineer`.
- Defaults: `pde_questions_crawled.html`, `pde_crawl_checkpoint.json`.
- UI strings / titles: Professional Data Engineer (not PCA).
- Keep Playwright + CAPTCHA-wait behavior unchanged.

### 2. Discussion fetcher

- Rename conceptually to PDE: file may become `fetch_pde_discussions.py` (or keep filename but retarget all PCA constants/regexes — prefer rename for clarity).
- Regex must match `/discussions/google/view/\d+-exam-professional-data-engineer-topic-\d+-question-\d+`.
- Defaults and generated titles use PDE naming (`pde_questions_*`).
- Update `tools/gcp_cert/tests/` accordingly.

### 3. Study app builder (`tools/gcp_cert/build_full_real_app.py`)

- Point `SOURCE` at the new PDE crawl/discussion JSON inside this repo (configurable path; no dependency on `/Users/.../GCP cerf`).
- Replace PCA case-study names / cue overrides with PDE-appropriate handling:
  - Prefer generic cue extraction from question text where possible.
  - Do not carry PCA case names (Altostrat, Cymbal, EHR, KnightMotives) into the PDE app.
- Output still writes the published root study files used by GitHub Pages.
- Branding: titles, `localStorage` key, service worker cache name, manifest name/description → PDE.

### 4. Published site (repo root)

- Rebuild `index.html` and `full-real-study-data.json` from PDE data.
- Update `README.md` to describe PDE study (not PCA).
- PCA-only mindmap / keyword files (`pca_exact_keyword_mindmap_*`, `exact-question-keywords.md`, older PCA JSON) are retired from the active product: stop linking them in README; leave deletion optional unless they confuse the app.

## Data flow

1. Run crawler (visible Chromium; user solves CAPTCHA if shown).
2. Produce `pde_questions_crawled.json` (+ HTML dump).
3. Run builder against that JSON to refresh GitHub Pages study assets.
4. Optionally run discussion fetcher later to refresh votes/new questions.

## Error handling

- CAPTCHA: existing poll-until-valid-page behavior.
- Checkpoint resume: keep `--resume` so interrupted crawls continue.
- Wrong-exam pages: discussion fetcher rejects non-PDE canonical URLs (same guard as PCA, new slug).

## Testing

- Update unit tests for PDE discussion URL accept/reject.
- Smoke: crawler dry-run / small `--pages N` before full crawl when useful.
- After full crawl: confirm question count is plausible (~349) and `index.html` titles say Professional Data Engineer.

## Out of scope

- Dual PCA + PDE site.
- New study UX beyond retargeting the existing answer-first app.
- Inventing PDE-specific mindmaps/keyword maps in this pass.

## Success criteria

- Tools and tests refer to Professional Data Engineer, not Professional Cloud Architect.
- Crawled data is from the PDE ExamTopics exam.
- Published `index.html` / study JSON are PDE-only and usable for study.
