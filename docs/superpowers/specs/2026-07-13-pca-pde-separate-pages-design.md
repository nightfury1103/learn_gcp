# Separate PCA + PDE Study Pages

**Date:** 2026-07-13  
**Status:** Approved  

## Goal

Keep the existing PCA study experience and add a separate Professional Data Engineer page limited to questions from **2024 to now**.

## Decisions

- **PCA:** restore and keep on `index.html` (+ existing PCA study JSON/reference).
- **PDE:** new `pde.html` (+ `pde-study-data.json` / reference), not overwriting PCA.
- **Year source:** parse from discussion-page `span.comment-date[title]` (missed in the first PDE fetch). Filter PDE study set to `year >= 2024`.

## Work

1. Restore PCA published assets from git HEAD.
2. Add year extraction to `fetch_pde_discussions.py` + unit test; refresh years on `pde_questions_crawled.json`.
3. Extend builder to emit PDE page/data from crawl JSON with `--min-year 2024`, without touching `index.html`.
4. Update README to link both pages.

## Success

- `index.html` is PCA again.
- `pde.html` is PDE-only, 2024–now, all discussion URLs `professional-data-engineer`.
- Every included PDE row has a non-null `year >= 2024`.
