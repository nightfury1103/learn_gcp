# GCP certification tooling

This folder contains the reusable Python tooling for the Professional Data
Engineer study pipeline. It is separate from the GitHub Pages files at the
repository root.

- `crawl_examtopics.py` crawls PDE question pages with Playwright and
  Beautiful Soup.
- `fetch_pde_discussions.py` refreshes PDE discussion data with Requests and
  Beautiful Soup.
- `build_full_real_app.py` rebuilds the **PDE** study page (`pde.html`) from a
  PDE question JSON file. It does **not** overwrite the PCA `index.html`.
  Default filter: `--min-year 2024`.

Install the dependency set needed for the script you run. The crawler also
requires a Playwright Chromium install.

```sh
pip install playwright beautifulsoup4 requests
python -m playwright install chromium
```

Run the regression tests from the repository root:

```sh
python3 -m unittest discover -s tools/gcp_cert/tests -v
```

Typical flow (preferred — discussion pages, no exam CAPTCHA):

```sh
# Bootstrap all PDE discussion URLs from the public Google discussions index,
# then hydrate each question (including year from comment-date) from its page.
python3 tools/gcp_cert/fetch_pde_discussions.py \
  --discover --scan 0 \
  --out pde_questions_crawled

# Build separate PDE study page (keeps PCA index.html intact)
python3 tools/gcp_cert/build_full_real_app.py --source pde_questions_crawled.json --min-year 2024
```

`crawl_examtopics.py` (Playwright exam pages) often hits CAPTCHA after a few
pages. Prefer `fetch_pde_discussions.py --discover` for a full PDE dump, which
matches the original PCA workflow in `Downloads/GCP cerf`.
