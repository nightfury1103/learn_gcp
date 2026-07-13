# GCP Cert Study Pages

Static GitHub Pages study apps for Google Cloud certifications.

## Pages

- [`index.html`](index.html) — Professional Cloud Architect (existing PCA study set)
- [`pde.html`](pde.html) — Professional Data Engineer, **2024 to now**

## Tooling

Crawler, discussion fetcher, builder, and tests live in
[`tools/gcp_cert`](tools/gcp_cert/).

Preferred PDE refresh (discussion pages, includes year from comment dates):

```sh
python3 tools/gcp_cert/fetch_pde_discussions.py --discover --scan 0 --out pde_questions_crawled
python3 tools/gcp_cert/build_full_real_app.py --source pde_questions_crawled.json --min-year 2024
```

Progress is stored in browser `localStorage` (separate keys per cert page).
