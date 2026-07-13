#!/usr/bin/env python3
from __future__ import annotations
"""
ExamTopics PDE — discussion-page fetcher (no CAPTCHA, no Playwright).

Strategy
--------
1. Preferred bootstrap: --discover scrapes /discussions/google/ for
   professional-data-engineer links, then hydrates each discussion page.
2. Or load an existing base JSON and re-fetch each known discussion URL so
   community votes/answers stay current.
3. Optionally scan disc_id values ABOVE the current maximum for brand-new
   questions. Scanning stops after MAX_CONSECUTIVE_MISSES consecutive IDs
   that contain no PDE question.

This matches the original PCA workflow under Downloads/GCP cerf: discussion
pages are the reliable path. Exam listing pages (/exams/.../view/) hit
CAPTCHA after a few pages and are not used for a full dump.

Requirements
------------
    pip install requests beautifulsoup4

Usage
-----
    python3 fetch_pde_discussions.py --discover --scan 0 --out pde_questions_crawled
    python3 fetch_pde_discussions.py --base pde_questions_crawled.json [options]

Options
    --discover          Bootstrap URLs from the Google discussions index
    --discover-pages N  Cap discussion-index pages during --discover
    --base    JSON file to start from          (default: pde_questions_crawled.json)
    --out     Output stem (no extension)       (default: pde_questions_YYYY-MM-DD)
    --scan    How many disc_ids above max to scan for new Qs (default: 3000)
    --delay   Seconds between requests         (default: 0.8)
    --misses  Stop scanning after N consecutive misses (default: 150)
    --no-refetch  Skip re-fetching existing questions (just scan/discover)
"""

import argparse
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.examtopics.com"
DISC_BASE = f"{BASE_URL}/discussions/google/view/"
DISCUSSION_INDEX = f"{BASE_URL}/discussions/google/"
PDE_DISCUSSION_PATH = re.compile(
    r"/discussions/google/view/\d+-exam-professional-data-engineer"
    r"-topic-\d+-question-\d+(?:-discussion)?/?$"
)
PDE_DISCUSSION_HREF = re.compile(
    r"/discussions/google/view/(\d+)-exam-professional-data-engineer"
    r"-topic-(\d+)-question-(\d+)(?:-discussion)?/?",
    re.IGNORECASE,
)
LAST_FETCH_URL = ""

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)


# ─────────────────────────────────────────────────────────────
# Parsing  (same logic as the Playwright crawler)
# ─────────────────────────────────────────────────────────────

def build_vote_str(vote_list: list) -> str:
    if not vote_list:
        return ""
    total = sum(v.get("vote_count", 0) for v in vote_list)
    if total == 0:
        return ""
    parts = [
        f"{v['voted_answers']} ({round(v['vote_count']/total*100)}%)"
        for v in sorted(vote_list, key=lambda x: -x.get("vote_count", 0))
    ]
    return " ".join(parts)


def is_pde_discussion_url(url: str) -> bool:
    return bool(PDE_DISCUSSION_PATH.search(url))


def canonical_url_from_soup(soup: BeautifulSoup) -> str:
    canonical = soup.find("link", rel="canonical")
    if canonical and canonical.get("href"):
        return canonical["href"]
    og_url = soup.find("meta", property="og:url")
    if og_url and og_url.get("content"):
        return og_url["content"]
    return ""


def image_options_from_question_tag(q_tag) -> list[dict]:
    options = []
    pending_label = ""
    seen = set()
    for node in q_tag.descendants:
        name = getattr(node, "name", None)
        if name == "img" and pending_label:
            src = node.get("src", "").strip()
            if src and pending_label not in seen:
                options.append({"label": pending_label, "text": f"Image: {src}"})
                seen.add(pending_label)
            pending_label = ""
            continue
        if name is not None:
            continue
        for label in re.findall(r"\b([A-Z])\.", str(node)):
            if label not in seen:
                pending_label = label
    return options


def extract_year_from_soup(soup: BeautifulSoup) -> int | None:
    """
    Prefer the first discussion comment date title, e.g.
    <span class="comment-date" title="Sat 14 Mar 2026 13:10">.
    Fall back to "at Month DD, YYYY" text near the question.
    """
    for el in soup.select("span.comment-date[title], .comment-date[title], span.post-date[title]"):
        title = el.get("title") or ""
        m = re.search(r"\b(20\d{2})\b", title)
        if m:
            return int(m.group(1))

    text = soup.get_text(" ", strip=True)
    m = re.search(
        r"\bat\s+(?:[A-Za-z]+\.?)\s+\d{1,2},\s+(20\d{2})",
        text,
    )
    if m:
        return int(m.group(1))
    return None


def parse_question_from_html(html: str, disc_id: int = 0, source_url: str = "") -> dict | None:
    """
    Parse one question from a discussion page or exam page.

    Discussion pages differ from exam pages:
      - No outer 'exam-question-card' wrapper
      - Question/Topic numbers appear as "Question #: N" / "Topic #: N" text
      - The data-id on question-body is a NEW internal id, not the disc_id

    Returns None if no valid question card is found.
    """
    soup = BeautifulSoup(html, "html.parser")
    canonical_url = canonical_url_from_soup(soup)
    if canonical_url and not is_pde_discussion_url(canonical_url):
        return None
    if source_url and not is_pde_discussion_url(source_url):
        return None

    # Detect format: exam page (has exam-question-card) or discussion page
    card = soup.find("div", class_="exam-question-card")
    if card:
        # ── Exam page format ──
        try:
            header = card.find("div", class_="card-header")
            if not header:
                return None
            htext = header.get_text(" ", strip=True)
            q_num_m = re.search(r"Question #(\d+)", htext)
            topic_m = re.search(r"Topic (\d+)", htext)
            if not q_num_m:
                return None
            q_num = int(q_num_m.group(1))
            topic = int(topic_m.group(1)) if topic_m else 1
            body = card.find("div", class_="question-body")
            if not body:
                return None
        except Exception:
            return None
    else:
        # ── Discussion page format ──
        # Question #: N and Topic #: N appear as plain text in the page
        full_text = soup.get_text(" ")
        q_num_m = re.search(r"Question #[:\s]+(\d+)", full_text)
        topic_m  = re.search(r"Topic #[:\s]+(\d+)",   full_text)
        if not q_num_m:
            return None
        q_num = int(q_num_m.group(1))
        topic = int(topic_m.group(1)) if topic_m else 1
        body = soup.find("div", class_="question-body")
        if not body:
            return None

    try:

        q_tag = body.find("p", class_="card-text")
        if not q_tag:
            return None
        for br in q_tag.find_all("br"):
            br.replace_with("\n")
        q_text = re.sub(r"\n{3,}", "\n\n", q_tag.get_text("", strip=True)).strip()

        options, correct = [], []
        for li in body.find_all("li", class_="multi-choice-item"):
            lspan = li.find("span", class_="multi-choice-letter")
            letter = (lspan.get("data-choice-letter") or "").strip() if lspan else ""
            if not letter:
                continue
            txt = re.sub(rf"^{letter}\.\s*", "", li.get_text(" ", strip=True)).strip()
            options.append({"label": letter, "text": txt})
            if "correct-hidden" in li.get("class", []):
                correct.append(letter)

        if not options:
            options = image_options_from_question_tag(q_tag)

        if not options:
            return None

        vs = body.find("script", type="application/json")
        vote_str = ""
        if vs and vs.string:
            try:
                vote_str = build_vote_str(json.loads(vs.string))
            except Exception:
                pass

        # For disc_url: prefer the disc_id passed in (from the URL we fetched),
        # fall back to data-id on the body element (works for exam-page format).
        url_id = disc_id if disc_id else body.get("data-id", "")
        disc_url = (
            f"{DISC_BASE}{url_id}-exam-professional-data-engineer"
            f"-topic-{topic}-question-{q_num}-discussion/"
            if url_id else ""
        )

        return {
            "topic": topic,
            "question_number": q_num,
            "year": extract_year_from_soup(soup),
            "url": disc_url,
            "question_text": q_text,
            "options": options,
            "suggested_answer": "".join(correct),
            "multi_answer": len(correct) > 1,
            "community_vote": vote_str,
        }
    except Exception as e:
        print(f"  ⚠ Parse error: {e}", file=sys.stderr)
        return None


# ─────────────────────────────────────────────────────────────
# HTTP helpers
# ─────────────────────────────────────────────────────────────

def fetch(url: str, retries: int = 3, delay: float = 2.0) -> str | None:
    global LAST_FETCH_URL
    LAST_FETCH_URL = url
    for attempt in range(1, retries + 1):
        try:
            r = SESSION.get(url, timeout=20, allow_redirects=True)
            LAST_FETCH_URL = r.url
            if r.status_code == 200:
                return r.text
            if r.status_code == 404:
                return None
            # Other error — back off
            time.sleep(delay * attempt)
        except Exception as e:
            if attempt == retries:
                print(f"  ✗ Fetch failed {url}: {e}", file=sys.stderr)
            time.sleep(delay * attempt)
    return None


def disc_url_from_id(disc_id: int, topic: int = 1, q_num: int = 1) -> str:
    slug = (
        f"{disc_id}-exam-professional-data-engineer"
        f"-topic-{topic}-question-{q_num}-discussion"
    )
    return f"{DISC_BASE}{slug}/"


# ─────────────────────────────────────────────────────────────
# Main logic
# ─────────────────────────────────────────────────────────────

def refetch_known(questions: list[dict], delay: float) -> list[dict]:
    """Re-fetch every question via its discussion page to get fresh data."""
    updated = []
    total = len(questions)
    for i, q in enumerate(questions, 1):
        url = q.get("url", "")
        if not url:
            updated.append(q)
            print(f"  [{i:3d}/{total}] T{q['topic']} Q{q['question_number']:3d} — no URL, kept as-is")
            continue

        html = fetch(url)
        if not html:
            updated.append(q)
            print(f"  [{i:3d}/{total}] T{q['topic']} Q{q['question_number']:3d} — fetch failed, kept old")
            time.sleep(delay)
            continue

        # Extract disc_id from the URL so the parser can use it for disc_url
        m_id = re.match(r".*/view/(\d+)-", url)
        did = int(m_id.group(1)) if m_id else 0
        parsed = parse_question_from_html(html, disc_id=did, source_url=LAST_FETCH_URL)
        if parsed:
            updated.append(parsed)
            changed = (
                parsed["suggested_answer"] != q["suggested_answer"] or
                parsed["community_vote"] != q["community_vote"]
            )
            mark = " ✎" if changed else ""
            print(f"  [{i:3d}/{total}] T{q['topic']} Q{q['question_number']:3d} — OK{mark}")
        else:
            updated.append(q)
            print(f"  [{i:3d}/{total}] T{q['topic']} Q{q['question_number']:3d} — parse failed, kept old")

        time.sleep(delay)

    return updated


def scan_new(max_id: int, scan_range: int, max_misses: int, delay: float) -> list[dict]:
    """Scan disc_ids above max_id for new PDE questions."""
    new_qs = []
    consecutive_misses = 0
    start = max_id + 1
    end = max_id + scan_range + 1

    print(f"\nScanning disc_ids {start}–{end - 1} for new questions…")
    print(f"(stopping after {max_misses} consecutive misses)\n")

    for disc_id in range(start, end):
        if consecutive_misses >= max_misses:
            print(f"  Reached {max_misses} consecutive misses — stopping scan.")
            break

        url = disc_url_from_id(disc_id)
        html = fetch(url)

        if not html:
            consecutive_misses += 1
            continue

        parsed = parse_question_from_html(html, disc_id=disc_id, source_url=LAST_FETCH_URL)
        if parsed:
            consecutive_misses = 0
            new_qs.append(parsed)
            print(
                f"  ✓ Found disc_id={disc_id}: "
                f"T{parsed['topic']} Q{parsed['question_number']} "
                f"(answer={parsed['suggested_answer']})"
            )
        else:
            # Page loaded but no PDE question card (different exam or junk)
            consecutive_misses += 1

        time.sleep(delay)

    return new_qs


def discussion_index_url(page_num: int) -> str:
    if page_num <= 1:
        return DISCUSSION_INDEX
    return f"{DISCUSSION_INDEX}{page_num}/"


def detect_discussion_index_last_page(delay: float = 0.3) -> int:
    """Binary-search the last valid /discussions/google/{n}/ page."""
    html = fetch(discussion_index_url(1))
    if not html:
        return 1
    time.sleep(delay)

    lo, hi = 1, 512
    last = 1
    while lo <= hi:
        mid = (lo + hi) // 2
        page_html = fetch(discussion_index_url(mid))
        ok = bool(page_html and "discussion-link" in page_html)
        if ok:
            last = mid
            lo = mid + 1
        else:
            hi = mid - 1
        time.sleep(delay)
    return last


def discover_from_discussion_index(
    delay: float = 0.35,
    max_pages: int | None = None,
) -> list[dict]:
    """
    Bootstrap PDE question URLs from the public Google discussions index.

    This avoids ExamTopics exam-page CAPTCHAs. Each hit becomes a stub row that
    refetch_known() can hydrate from the discussion page.
    """
    last_page = max_pages or detect_discussion_index_last_page(delay=delay)
    print(f"\nDiscovering PDE links from discussion index (pages 1–{last_page})…")

    found: dict[tuple[int, int], dict] = {}
    for page_num in range(1, last_page + 1):
        html = fetch(discussion_index_url(page_num))
        if not html:
            print(f"  Page {page_num}/{last_page} — fetch failed")
            time.sleep(delay)
            continue

        page_hits = 0
        for match in PDE_DISCUSSION_HREF.finditer(html):
            disc_id = int(match.group(1))
            topic = int(match.group(2))
            q_num = int(match.group(3))
            url = (
                f"{DISC_BASE}{disc_id}-exam-professional-data-engineer"
                f"-topic-{topic}-question-{q_num}-discussion/"
            )
            key = (topic, q_num)
            if key not in found:
                found[key] = {
                    "topic": topic,
                    "question_number": q_num,
                    "url": url,
                    "question_text": "",
                    "options": [],
                    "suggested_answer": "",
                    "multi_answer": False,
                    "community_vote": "",
                }
                page_hits += 1

        print(
            f"  Page {page_num:3d}/{last_page} — "
            f"+{page_hits} new PDE links (total {len(found)})"
        )
        time.sleep(delay)

    questions = sorted(found.values(), key=lambda q: (q["topic"], q["question_number"]))
    print(f"Discovery done — {len(questions)} unique PDE discussion URLs")
    return questions


# ─────────────────────────────────────────────────────────────
# HTML / JSON output
# ─────────────────────────────────────────────────────────────

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg:#f0f4f8; --card:#fff; --primary:#1a73e8; --primary-dk:#1557b0;
  --ok:#34a853; --err:#ea4335; --text:#202124; --muted:#5f6368;
  --border:#dadce0; --r:12px;
  --shadow:0 1px 3px rgba(0,0,0,.1),0 4px 12px rgba(0,0,0,.06);
}
body { font-family:"Google Sans","Segoe UI",Roboto,Arial,sans-serif;
       background:var(--bg); color:var(--text); min-height:100vh; }
header { background:var(--primary); color:#fff; padding:18px 24px 14px;
         position:sticky; top:0; z-index:100;
         box-shadow:0 2px 8px rgba(0,0,0,.22); }
header h1 { font-size:1.2rem; font-weight:600; }
header p  { font-size:.82rem; opacity:.82; margin-top:2px; }
.toolbar { background:#fff; border-bottom:1px solid var(--border);
           padding:10px 24px; display:flex; flex-wrap:wrap; gap:10px;
           align-items:center; position:sticky; top:56px; z-index:99; }
.search-box { flex:1; min-width:180px; max-width:360px; padding:7px 14px;
              border:1.5px solid var(--border); border-radius:24px;
              font-size:.88rem; outline:none; transition:border-color .2s; }
.search-box:focus { border-color:var(--primary); }
.topic-filters, .year-filters { display:flex; flex-wrap:wrap; gap:6px; }
.filter-btn { padding:5px 13px; border:1.5px solid var(--border);
             border-radius:20px; background:#fff; font-size:.8rem;
             cursor:pointer; transition:all .15s; white-space:nowrap; }
.filter-btn:hover { border-color:var(--primary); color:var(--primary); }
.filter-btn.active { background:var(--primary); color:#fff; border-color:var(--primary); }
.badge { background:var(--bg); border-radius:10px; padding:0 6px;
         font-size:.73rem; margin-left:3px; color:var(--muted); }
.filter-btn.active .badge { background:rgba(255,255,255,.22); color:#fff; }
.stats-bar { padding:8px 24px; font-size:.8rem; color:var(--muted); }
main { padding:12px 24px 48px; max-width:940px; margin:0 auto;
       display:flex; flex-direction:column; gap:14px; }
.card { background:var(--card); border-radius:var(--r);
        box-shadow:var(--shadow); padding:18px 22px;
        border:1px solid var(--border); }
.card-header { display:flex; align-items:center; gap:8px; margin-bottom:12px; }
.q-label { font-size:.72rem; font-weight:700; letter-spacing:.5px;
           text-transform:uppercase; color:var(--primary);
           background:#e8f0fe; padding:3px 10px; border-radius:20px; }
.q-num { font-size:.8rem; color:var(--muted); font-weight:500; }
.year-tag { font-size:.72rem; font-weight:700; color:#137333;
            background:#e6f4ea; padding:3px 10px; border-radius:20px; }
.multi-tag { font-size:.68rem; font-weight:600; letter-spacing:.4px;
             text-transform:uppercase; color:#e37400;
             background:#fef7e0; padding:2px 8px; border-radius:20px; }
.src-link { margin-left:auto; font-size:.76rem; color:var(--primary);
            text-decoration:none; opacity:.65; transition:opacity .15s; }
.src-link:hover { opacity:1; }
.question-text { font-size:.95rem; line-height:1.68; margin-bottom:14px;
                 white-space:pre-wrap; }
.options { display:flex; flex-direction:column; gap:7px; margin-bottom:14px; }
.option {
  display:flex; align-items:flex-start; gap:9px; padding:9px 13px;
  border-radius:8px; border:1.5px solid var(--border); cursor:pointer;
  transition:background .12s,border-color .12s; font-size:.88rem;
  line-height:1.5; user-select:none;
}
.option:hover { border-color:var(--primary); background:#f0f4ff; }
.option.selected { background:#e8f0fe; border-color:var(--primary); }
.option.selected .opt-label { color:var(--primary); }
.option.correct { background:#e6f4ea; border-color:var(--ok); }
.option.correct .opt-label { color:var(--ok); }
.option.wrong { background:#fce8e6; border-color:var(--err); }
.option.wrong .opt-label { color:var(--err); }
.options.revealed .option { cursor:default; }
.options.revealed .option:not(.correct):not(.wrong):hover
  { background:#fff; border-color:var(--border); }
.opt-label { font-weight:700; min-width:20px; color:var(--muted); transition:color .12s; }
.opt-ind {
  width:17px; height:17px; min-width:17px; margin-top:2px;
  border:2px solid var(--border); transition:all .12s;
  display:flex; align-items:center; justify-content:center;
}
.opt-ind.radio { border-radius:50%; }
.option.selected .opt-ind.radio,
.option.correct  .opt-ind.radio,
.option.wrong    .opt-ind.radio { background:currentColor; border-color:currentColor; }
.opt-ind.checkbox { border-radius:4px; }
.option.selected .opt-ind.checkbox { background:var(--primary); border-color:var(--primary); }
.option.correct  .opt-ind.checkbox { background:var(--ok); border-color:var(--ok); }
.option.wrong    .opt-ind.checkbox { background:var(--err); border-color:var(--err); }
.opt-ind::after { content:''; display:none; width:6px; height:6px; border-radius:50%; background:#fff; }
.opt-ind.radio::after { display:block; opacity:0; transition:opacity .12s; }
.option.selected .opt-ind.radio::after,
.option.correct  .opt-ind.radio::after,
.option.wrong    .opt-ind.radio::after { opacity:1; }
.opt-ind.checkbox::after { content:'✓'; display:none; color:#fff; font-size:11px;
  font-weight:700; width:auto; height:auto; border-radius:0; background:transparent; }
.option.selected .opt-ind.checkbox::after,
.option.correct  .opt-ind.checkbox::after,
.option.wrong    .opt-ind.checkbox::after { display:block; }
.answer-row { display:flex; align-items:center; gap:9px; flex-wrap:wrap; }
.show-btn { padding:6px 17px; background:var(--primary); color:#fff; border:none;
  border-radius:20px; font-size:.83rem; cursor:pointer;
  transition:background .15s; font-weight:500; }
.show-btn:hover { background:var(--primary-dk); }
.show-btn.hide-mode { background:#5f6368; }
.show-btn.hide-mode:hover { background:#3c4043; }
.answer-badge { display:none; align-items:center; gap:5px; font-size:.85rem;
  font-weight:600; padding:4px 13px; border-radius:20px; }
.answer-badge.visible { display:flex; }
.ok-badge  { color:var(--ok);  background:#e6f4ea; }
.err-badge { color:var(--err); background:#fce8e6; }
.vote-box { display:none; margin-top:10px; padding:8px 13px; background:#f8f9fa;
  border-radius:8px; border:1px solid var(--border); font-size:.82rem; color:var(--muted); }
.vote-box.visible { display:block; }
.vote-label { font-weight:600; display:inline; }
.no-results { text-align:center; padding:48px; color:var(--muted); font-size:1rem; }
"""

JS = r"""
const DATA = __DATA__;
let activeTopic = 0;
let activeYearRange = 'all';
const state = {};

function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
function getKey(q) { return `${q.topic}_${q.question_number}`; }

window.onload = function() { buildTopicFilters(); buildYearFilters(); applyFilters(); };

function buildTopicFilters() {
  const counts = {};
  DATA.forEach(q => { counts[q.topic] = (counts[q.topic]||0)+1; });
  const topics = Object.keys(counts).map(Number).sort((a,b)=>a-b);
  let html = `<button class="filter-btn topic-btn active" onclick="setTopic(0,this)">All <span class="badge">${DATA.length}</span></button>`;
  topics.forEach(t => {
    html += `<button class="filter-btn topic-btn" onclick="setTopic(${t},this)">Topic ${t} <span class="badge">${counts[t]}</span></button>`;
  });
  document.getElementById('topicFilters').innerHTML = html;
}

function buildYearFilters() {
  const currentYear = new Date().getFullYear();
  const recentCount = DATA.filter(q => Number(q.year) >= 2024 && Number(q.year) <= currentYear).length;
  let html = `<button class="filter-btn year-btn active" onclick="setYearRange('all',this)">All Dates <span class="badge">${DATA.length}</span></button>`;
  html += `<button class="filter-btn year-btn" onclick="setYearRange('recent',this)">2024-Now <span class="badge">${recentCount}</span></button>`;
  document.getElementById('yearFilters').innerHTML = html;
}

function setTopic(t, btn) {
  activeTopic = t;
  document.querySelectorAll('.topic-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}

function setYearRange(range, btn) {
  activeYearRange = range;
  document.querySelectorAll('.year-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}

function applyFilters() {
  const q = (document.getElementById('searchBox').value||'').toLowerCase();
  let items = DATA;
  if (activeTopic) items = items.filter(x => x.topic === activeTopic);
  if (activeYearRange === 'recent') {
    const currentYear = new Date().getFullYear();
    items = items.filter(x => Number(x.year) >= 2024 && Number(x.year) <= currentYear);
  }
  if (q) items = items.filter(x =>
    x.question_text.toLowerCase().includes(q) ||
    (x.options||[]).some(o => o.text.toLowerCase().includes(q))
  );
  document.getElementById('statsBar').textContent =
    `Showing ${items.length} of ${DATA.length} questions`;
  if (!items.length) {
    document.getElementById('main').innerHTML = '<div class="no-results">No questions found.</div>';
    return;
  }
  document.getElementById('main').innerHTML = items.map(q => {
    const key = getKey(q);
    const isMulti = q.multi_answer;
    const indCls = isMulti ? 'checkbox' : 'radio';
    const opts = (q.options||[]).map(o => `
      <div class="option" id="opt-${key}-${o.label}"
           onclick="selectOption('${key}','${o.label}','${esc(q.suggested_answer)}',${isMulti})">
        <span class="opt-ind ${indCls}"></span>
        <span class="opt-label">${o.label}.</span>
        <span>${esc(o.text)}</span>
      </div>`).join('');
    const multiTag = isMulti
      ? `<span class="multi-tag">Choose ${q.suggested_answer.length} answer(s)</span>` : '';
    const srcLink = q.url
      ? `<a class="src-link" href="${q.url}" target="_blank">Source ↗</a>` : '';
    const yearTag = q.year ? `<span class="year-tag">${q.year}</span>` : '';
    const vote = q.community_vote
      ? `<div class="vote-box" id="vote-${key}"><span class="vote-label">Community Vote:</span> ${esc(q.community_vote)}</div>` : '';
    return `
    <div class="card">
      <div class="card-header">
        <span class="q-label">Topic ${q.topic}</span>
        <span class="q-num">Question #${q.question_number}</span>
        ${yearTag}${multiTag}${srcLink}
      </div>
      <div class="question-text">${esc(q.question_text)}</div>
      <div class="options" id="opts-${key}">${opts}</div>
      <div class="answer-row">
        <button class="show-btn" id="btn-${key}"
          onclick="toggleAnswer('${key}','${esc(q.suggested_answer)}')">
          Show Answer
        </button>
        <div class="answer-badge" id="ans-${key}"></div>
      </div>
      ${vote}
    </div>`;
  }).join('');
}

function getState(key) {
  if (!state[key]) state[key] = { selected: new Set(), revealed: false };
  return state[key];
}

function selectOption(key, letter, correct, isMulti) {
  const st = getState(key);
  if (st.revealed) return;
  if (isMulti) {
    const el = document.getElementById(`opt-${key}-${letter}`);
    if (st.selected.has(letter)) { st.selected.delete(letter); el&&el.classList.remove('selected'); }
    else { st.selected.add(letter); el&&el.classList.add('selected'); }
  } else {
    if (st.selected.size) {
      const prev = [...st.selected][0];
      const pe = document.getElementById(`opt-${key}-${prev}`);
      pe&&pe.classList.remove('selected');
    }
    st.selected = new Set([letter]);
    const el = document.getElementById(`opt-${key}-${letter}`);
    el&&el.classList.add('selected');
  }
}

function toggleAnswer(key, correct) {
  const st = getState(key);
  const btn = document.getElementById(`btn-${key}`);
  const badge = document.getElementById(`ans-${key}`);
  const vote = document.getElementById(`vote-${key}`);
  const optsEl = document.getElementById(`opts-${key}`);
  const cs = new Set(correct.split(''));
  if (!st.revealed) {
    st.revealed = true;
    optsEl.classList.add('revealed');
    cs.forEach(c => {
      const el = document.getElementById(`opt-${key}-${c}`);
      el&&(el.classList.remove('selected'), el.classList.add('correct'));
    });
    st.selected.forEach(s => {
      if (!cs.has(s)) { const el=document.getElementById(`opt-${key}-${s}`); el&&el.classList.add('wrong'); }
    });
    badge.className = 'answer-badge ok-badge visible';
    badge.textContent = 'Answer: ' + correct;
    if (vote) vote.classList.add('visible');
    btn.textContent = 'Hide Answer';
    btn.classList.add('hide-mode');
  } else {
    st.revealed = false;
    optsEl.classList.remove('revealed');
    optsEl.querySelectorAll('.option').forEach(el => {
      el.classList.remove('correct','wrong');
      const ltr = el.id.split('-').pop();
      if (st.selected.has(ltr)) el.classList.add('selected');
    });
    badge.className = 'answer-badge';
    if (vote) vote.classList.remove('visible');
    btn.textContent = 'Show Answer';
    btn.classList.remove('hide-mode');
  }
}
"""


def build_html(questions: list[dict], out_path: str):
    data_json = json.dumps(questions, ensure_ascii=False, separators=(",", ":"))
    data_json = (
        data_json
        .replace("<", r"\u003c")
        .replace(">", r"\u003e")
        .replace("&", r"\u0026")
    )
    js = JS.replace("__DATA__", data_json)
    html = (
        f'<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        f'<meta charset="UTF-8">\n'
        f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>GCP PDE — {len(questions)} Questions</title>\n'
        f'<style>\n{CSS}\n</style>\n'
        f'</head>\n<body>\n'
        f'<header>\n'
        f'  <h1>GCP Professional Data Engineer — Exam Questions</h1>\n'
        f'  <p>Refreshed from ExamTopics · {len(questions)} questions · {date.today().isoformat()}</p>\n'
        f'</header>\n'
        f'<div class="toolbar">\n'
        f'  <input class="search-box" id="searchBox" type="search" '
        f'placeholder="Search questions…" oninput="applyFilters()">\n'
        f'  <div class="topic-filters" id="topicFilters"></div>\n'
        f'  <div class="year-filters" id="yearFilters"></div>\n'
        f'</div>\n'
        f'<div class="stats-bar" id="statsBar">Loading…</div>\n'
        f'<main id="main"></main>\n'
        f'<script>\n{js}\n</script>\n'
        f'</body>\n</html>\n'
    )
    Path(out_path).write_text(html, encoding="utf-8")
    print(f"Saved HTML → {out_path} ({Path(out_path).stat().st_size // 1024} KB)")


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="Fetch ExamTopics Professional Data Engineer discussion pages."
    )
    ap.add_argument("--base", default="pde_questions_crawled.json")
    ap.add_argument("--out", default=f"pde_questions_{date.today().isoformat()}")
    ap.add_argument("--scan", type=int, default=3000,
                    help="How many disc_ids above the current max to scan")
    ap.add_argument("--delay", type=float, default=0.8)
    ap.add_argument("--misses", type=int, default=150,
                    help="Stop scanning after N consecutive misses")
    ap.add_argument("--no-refetch", action="store_true",
                    help="Skip re-fetching existing questions")
    ap.add_argument(
        "--discover",
        action="store_true",
        help="Bootstrap URLs from /discussions/google/ index (no exam-page CAPTCHA)",
    )
    ap.add_argument(
        "--discover-pages",
        type=int,
        default=None,
        help="Optional max discussion-index pages to crawl during --discover",
    )
    args = ap.parse_args()

    print("=" * 62)
    print("  ExamTopics PDE — Discussion-Page Fetcher")
    print("=" * 62)

    questions: list[dict] = []
    base_path = Path(args.base)

    if args.discover:
        questions = discover_from_discussion_index(
            delay=min(args.delay, 0.5),
            max_pages=args.discover_pages,
        )
        if base_path.exists():
            with open(base_path, encoding="utf-8") as f:
                existing = json.load(f)
            print(f"  Merging with base {args.base} ({len(existing)} questions)")
            by_key = {(q["topic"], q["question_number"]): q for q in existing}
            for q in questions:
                by_key[(q["topic"], q["question_number"])] = q
            questions = sorted(by_key.values(), key=lambda q: (q["topic"], q["question_number"]))
    else:
        if not base_path.exists():
            print(f"Base file not found: {base_path}", file=sys.stderr)
            print("Hint: re-run with --discover to bootstrap from the discussions index.", file=sys.stderr)
            sys.exit(1)
        with open(base_path, encoding="utf-8") as f:
            questions = json.load(f)
        print(f"  Base: {args.base} — {len(questions)} questions loaded")

    # Find max disc_id from existing questions
    max_disc_id = 0
    for q in questions:
        m = re.match(r".*/view/(\d+)-", q.get("url", ""))
        if m:
            max_disc_id = max(max_disc_id, int(m.group(1)))
    print(f"  Max disc_id in base: {max_disc_id}")
    print()

    # Phase 1: re-fetch existing questions
    if not args.no_refetch:
        print(f"Phase 1 — Re-fetching {len(questions)} existing questions via discussion pages…")
        print("(✎ = answer or vote changed vs. base)\n")
        questions = refetch_known(questions, args.delay)
        # Deduplicate by (topic, question_number), keep latest
        seen = {}
        for q in questions:
            if not q.get("question_text") and not q.get("options"):
                # Keep empty stubs out if parse failed and they were empty
                key = (q["topic"], q["question_number"])
                if key in seen and seen[key].get("question_text"):
                    continue
            seen[(q["topic"], q["question_number"])] = q
        questions = sorted(
            [q for q in seen.values() if q.get("question_text") and q.get("options")],
            key=lambda q: (q["topic"], q["question_number"]),
        )
        print(f"\nPhase 1 done — {len(questions)} questions")
    else:
        print("Phase 1 skipped (--no-refetch).")

    # Phase 2: scan for new questions
    if args.scan > 0 and max_disc_id > 0:
        print(f"\nPhase 2 — Scanning for new questions (disc_ids {max_disc_id + 1} → {max_disc_id + args.scan})…")
        new_qs = scan_new(max_disc_id, args.scan, args.misses, args.delay)
        if new_qs:
            print(f"\nPhase 2 done — found {len(new_qs)} new questions!")
            questions.extend(new_qs)
            seen = {}
            for q in questions:
                seen[(q["topic"], q["question_number"])] = q
            questions = sorted(seen.values(), key=lambda q: (q["topic"], q["question_number"]))
        else:
            print("\nPhase 2 done — no new questions found.")
    else:
        print("Phase 2 skipped (--scan 0 or no max disc_id).")

    print(f"\nTotal: {len(questions)} questions")

    # Save outputs
    html_out = args.out + ".html"
    json_out = args.out + ".json"

    build_html(questions, html_out)

    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    print(f"Saved JSON → {json_out} ({Path(json_out).stat().st_size // 1024} KB)")
    print("\nDone!")


if __name__ == "__main__":
    main()
