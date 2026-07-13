#!/usr/bin/env python3
from __future__ import annotations
"""
ExamTopics PDE Crawler  — uses a real (visible) Chromium browser.
You keep the browser window open; the script handles navigation and parsing.
If the site shows a CAPTCHA / Validation page, just solve it yourself in the
browser — the script watches the page and continues automatically once it
detects real exam content (no Enter key needed).

Requirements:
    pip install playwright beautifulsoup4
    python -m playwright install chromium

Usage:
    python3 crawl_examtopics.py [options]

Options:
    --out FILE      Output HTML file   (default: pde_questions_crawled.html)
    --delay SECS    Pause between pages (default: 3.0)
    --headless      Run without opening a browser window (may hit CAPTCHAs)
    --resume FILE   Checkpoint JSON file (default: pde_crawl_checkpoint.json)
    --pages N       Stop after N pages  (default: auto-detect all pages)
    --captcha-wait  Max seconds to wait for you to solve a CAPTCHA (default: 300)
"""

import argparse
import json
import math
import re
import sys
import time
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout


# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────
BASE_URL = (
    "https://www.examtopics.com/exams/google/"
    "professional-data-engineer/view/"
)
PAGE_URL = lambda n: BASE_URL if n == 1 else f"{BASE_URL}{n}/"

# ─────────────────────────────────────────────────────────────
# Parsing
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


def parse_html(html: str, page_num: int) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    questions = []

    for card in soup.find_all("div", class_="exam-question-card"):
        try:
            header = card.find("div", class_="card-header")
            if not header:
                continue
            htext = header.get_text(" ", strip=True)
            q_num_m = re.search(r"Question #(\d+)", htext)
            topic_m = re.search(r"Topic (\d+)", htext)
            if not q_num_m:
                continue
            q_num = int(q_num_m.group(1))
            topic = int(topic_m.group(1)) if topic_m else 1

            body = card.find("div", class_="question-body")
            if not body:
                continue

            # Question text (preserve newlines from <br>)
            q_tag = body.find("p", class_="card-text")
            if not q_tag:
                continue
            for br in q_tag.find_all("br"):
                br.replace_with("\n")
            q_text = re.sub(r"\n{3,}", "\n\n", q_tag.get_text("", strip=True)).strip()

            # Options + correct answer
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
                continue

            # Community vote
            vs = body.find("script", type="application/json")
            vote_str = ""
            if vs and vs.string:
                try:
                    vote_str = build_vote_str(json.loads(vs.string))
                except Exception:
                    pass

            data_id = body.get("data-id", "")
            disc_url = (
                f"https://www.examtopics.com/discussions/google/view/"
                f"{data_id}-exam-professional-data-engineer-topic-{topic}-question-{q_num}/"
                if data_id else ""
            )

            questions.append({
                "topic": topic,
                "question_number": q_num,
                "url": disc_url,
                "question_text": q_text,
                "options": options,
                "suggested_answer": "".join(correct),
                "multi_answer": len(correct) > 1,
                "community_vote": vote_str,
            })
        except Exception as e:
            print(f"  ⚠ Parse error (page {page_num}): {e}", file=sys.stderr)

    return questions


def is_validation_page(html: str) -> bool:
    """
    Returns True when the server returned a CAPTCHA/validation page
    instead of the real exam questions page.
    We detect the real page by looking for actual question card markup.
    """
    # The real exam page always contains these CSS class names
    return "exam-question-card" not in html or "multi-choice-item" not in html


def detect_last_page(html: str) -> int:
    """
    Try several patterns to find the total question count, then compute pages.
    Falls back to pagination link scanning.
    """
    # Pattern 1: inline "346 Questions & Answers" (some page variants)
    m = re.search(r"(\d{2,4})\s+Questions?\s*(?:&amp;|&)\s*Answers?", html, re.IGNORECASE)
    if m:
        return math.ceil(int(m.group(1)) / 10)

    # Pattern 2: <span>346</span> … <span>Questions…</span>  (most common live layout)
    m = re.search(
        r"<span[^>]*>\s*(\d{2,4})\s*</span>\s*<span[^>]*>\s*Questions?\s*(?:&amp;|&)\s*Answers?",
        html, re.IGNORECASE,
    )
    if m:
        return math.ceil(int(m.group(1)) / 10)

    # Pattern 3: "Viewing questions 1-10 out of 346 questions"
    m = re.search(r"out of (\d{2,4})\s+questions?", html, re.IGNORECASE)
    if m:
        return math.ceil(int(m.group(1)) / 10)

    # Pattern 4: highest page number in pagination links
    # ExamTopics paginates as /view/2/, /view/3/, … but only shows a few at a time.
    # The last visible page number underestimates the total, so we can't rely on it alone.
    # Use it as a minimum and add a large buffer to avoid stopping early.
    nums = [int(n) for n in re.findall(r"/view/(\d+)/", html)]
    if nums:
        return max(nums) + 33   # conservative upper bound (enough for 346 Qs)

    return 35  # hard-coded safe default for this exam


# ─────────────────────────────────────────────────────────────
# Crawler
# ─────────────────────────────────────────────────────────────
def wait_for_valid_page(
    page, url: str, page_num: int, headless: bool, delay: float, captcha_wait: int
) -> str | None:
    """
    Navigate to `url`, return the page HTML once it contains real exam content.

    If a CAPTCHA / validation page is detected:
      - headless=False: print a notice and then **poll** the live browser DOM
        every 2 s until real content appears (up to `captcha_wait` seconds).
        You just solve the CAPTCHA in the browser; no Enter key needed.
      - headless=True: wait and retry up to 3 times automatically.

    Returns None if the page never became valid.
    """
    max_retries = 4
    for attempt in range(1, max_retries + 1):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        except PWTimeout:
            print(f"    Timeout on {url} (attempt {attempt})", file=sys.stderr)
            time.sleep(delay * 2)
            continue

        time.sleep(1.5)  # Let JS settle

        html = page.content()
        if not is_validation_page(html):
            return html

        # ── CAPTCHA detected ──
        if not headless:
            print(
                f"\n  ⚠  CAPTCHA / Validation on page {page_num}.\n"
                f"     Solve it in the Chromium window — the script will\n"
                f"     continue automatically once the page loads. "
                f"(timeout: {captcha_wait}s)",
                flush=True,
            )
            # Poll the live DOM every 2 s — no keyboard input required
            deadline = time.time() + captcha_wait
            dots = 0
            while time.time() < deadline:
                time.sleep(2)
                try:
                    html = page.content()
                except Exception:
                    continue
                if not is_validation_page(html):
                    print("  ✓ CAPTCHA passed — continuing.", flush=True)
                    return html
                dots += 1
                if dots % 10 == 0:
                    remaining = int(deadline - time.time())
                    print(f"    Still waiting… ({remaining}s left)", flush=True)

            print(
                f"  ✗ Timed out waiting for CAPTCHA on page {page_num}.",
                file=sys.stderr,
            )
            return None  # Give up on this page

        else:
            # Headless: wait and retry with back-off
            wait_secs = delay * 3 * attempt
            print(
                f"    Validation page (attempt {attempt}/{max_retries})"
                f" — retrying in {wait_secs:.0f}s…"
            )
            time.sleep(wait_secs)

    return None


def crawl(args) -> list[dict]:
    checkpoint_path = args.resume

    # Load checkpoint
    checkpoint: dict[str, list] = {}
    if Path(checkpoint_path).exists():
        with open(checkpoint_path, encoding="utf-8") as f:
            checkpoint = json.load(f)
        print(f"Resuming — {len(checkpoint)} pages already in checkpoint.")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=args.headless,
            args=["--window-size=1280,900"],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = context.new_page()

        # ── Detect total pages (and seed checkpoint for page 1) ──
        max_pages = args.pages
        if max_pages is None or "1" not in checkpoint:
            print("Fetching page 1 to detect total…", end=" ", flush=True)
            html1 = wait_for_valid_page(page, PAGE_URL(1), 1, args.headless, args.delay, args.captcha_wait)
            if html1 is None:
                print("Failed to load page 1 — aborting.", file=sys.stderr)
                sys.exit(1)
            max_pages = max_pages or detect_last_page(html1)
            print(f"{max_pages} pages total.")
            if "1" not in checkpoint:
                checkpoint["1"] = parse_html(html1, 1)
                _save(checkpoint, checkpoint_path)
            time.sleep(args.delay)

        all_qs: list[dict] = []
        for p_num in range(1, max_pages + 1):
            key = str(p_num)
            if key in checkpoint:
                all_qs.extend(checkpoint[key])
                print(f"  Page {p_num:3d}/{max_pages} — cache  ({len(checkpoint[key])} Qs)")
                continue

            url = PAGE_URL(p_num)
            print(f"  Page {p_num:3d}/{max_pages} — {url} …", end=" ", flush=True)
            html = wait_for_valid_page(page, url, p_num, args.headless, args.delay, args.captcha_wait)
            if html is None:
                print(f"SKIPPED (validation not resolved after retries)")
            else:
                qs = parse_html(html, p_num)
                print(f"{len(qs)} Qs")
                checkpoint[key] = qs
                all_qs.extend(qs)
                _save(checkpoint, checkpoint_path)

            time.sleep(args.delay)

        browser.close()

    all_qs.sort(key=lambda q: (q["topic"], q["question_number"]))
    return all_qs


def _save(checkpoint, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────
# HTML output
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
.topic-filters { display:flex; flex-wrap:wrap; gap:6px; }
.topic-btn { padding:5px 13px; border:1.5px solid var(--border);
             border-radius:20px; background:#fff; font-size:.8rem;
             cursor:pointer; transition:all .15s; white-space:nowrap; }
.topic-btn:hover { border-color:var(--primary); color:var(--primary); }
.topic-btn.active { background:var(--primary); color:#fff; border-color:var(--primary); }
.badge { background:var(--bg); border-radius:10px; padding:0 6px;
         font-size:.73rem; margin-left:3px; color:var(--muted); }
.topic-btn.active .badge { background:rgba(255,255,255,.22); color:#fff; }
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
.vote-box { margin-top:10px; padding:8px 13px; background:#f8f9fa;
  border-radius:8px; border:1px solid var(--border); font-size:.82rem; color:var(--muted); }
.vote-label { font-weight:600; display:inline; }
.no-results { text-align:center; padding:48px; color:var(--muted); font-size:1rem; }
"""

JS = r"""
const DATA = __DATA__;
let activeTopic = 0;
const state = {};

function esc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
function getKey(q) { return `${q.topic}_${q.question_number}`; }

window.onload = function() { buildTopicFilters(); applyFilters(); };

function buildTopicFilters() {
  const counts = {};
  DATA.forEach(q => { counts[q.topic] = (counts[q.topic]||0)+1; });
  const topics = Object.keys(counts).map(Number).sort((a,b)=>a-b);
  let html = `<button class="topic-btn active" onclick="setTopic(0,this)">All <span class="badge">${DATA.length}</span></button>`;
  topics.forEach(t => {
    html += `<button class="topic-btn" onclick="setTopic(${t},this)">Topic ${t} <span class="badge">${counts[t]}</span></button>`;
  });
  document.getElementById('topicFilters').innerHTML = html;
}

function setTopic(t, btn) {
  activeTopic = t;
  document.querySelectorAll('.topic-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  applyFilters();
}

function applyFilters() {
  const q = (document.getElementById('searchBox').value||'').toLowerCase();
  let items = DATA;
  if (activeTopic) items = items.filter(x => x.topic === activeTopic);
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
    const vote = q.community_vote
      ? `<div class="vote-box"><span class="vote-label">Community Vote:</span> ${esc(q.community_vote)}</div>` : '';
    return `
    <div class="card">
      <div class="card-header">
        <span class="q-label">Topic ${q.topic}</span>
        <span class="q-num">Question #${q.question_number}</span>
        ${multiTag}${srcLink}
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
    btn.textContent = 'Show Answer';
    btn.classList.remove('hide-mode');
  }
}
"""


def build_html(questions: list[dict], out_path: str):
    data_json = json.dumps(questions, ensure_ascii=False, separators=(",", ":"))
    # Escape chars that would break the surrounding <script> block.
    # JSON \uXXXX escapes are decoded by the JS engine, so the data is intact.
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
        f'  <p>Crawled from ExamTopics · {len(questions)} questions · {date.today().isoformat()}</p>\n'
        f'</header>\n'
        f'<div class="toolbar">\n'
        f'  <input class="search-box" id="searchBox" type="search" '
        f'placeholder="Search questions…" oninput="applyFilters()">\n'
        f'  <div class="topic-filters" id="topicFilters"></div>\n'
        f'</div>\n'
        f'<div class="stats-bar" id="statsBar">Loading…</div>\n'
        f'<main id="main"></main>\n'
        f'<script>\n{js}\n</script>\n'
        f'</body>\n</html>\n'
    )

    Path(out_path).write_text(html, encoding="utf-8")
    kb = Path(out_path).stat().st_size / 1024
    print(f"\nSaved {len(questions)} questions → {out_path} ({kb:.0f} KB)")


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Crawl ExamTopics PDE questions.")
    ap.add_argument("--out", default="pde_questions_crawled.html")
    ap.add_argument("--delay", type=float, default=3.0,
                    help="Seconds between page requests (default 3.0)")
    ap.add_argument("--headless", action="store_true",
                    help="Run without browser window (may hit CAPTCHAs)")
    ap.add_argument("--resume", default="pde_crawl_checkpoint.json",
                    help="Checkpoint file (supports resuming interrupted runs)")
    ap.add_argument("--pages", type=int, default=None,
                    help="Max pages to crawl (default: auto-detect)")
    ap.add_argument("--captcha-wait", type=int, default=300,
                    help="Max seconds to wait for you to solve a CAPTCHA (default: 300)")
    args = ap.parse_args()

    mode = "headless" if args.headless else "visible browser"
    print("=" * 62)
    print("  ExamTopics PDE Crawler")
    print("=" * 62)
    print(f"  Mode      : {mode}")
    print(f"  Output    : {args.out}")
    print(f"  Delay     : {args.delay}s")
    print(f"  Checkpoint: {args.resume}")
    if not args.headless:
        print()
        print("  A Chromium window will open. Keep it visible.")
        print("  If a CAPTCHA appears, just solve it in the browser.")
        print("  The script watches automatically — no Enter key needed.")
    print()

    questions = crawl(args)

    if not questions:
        print("No questions found.", file=sys.stderr)
        sys.exit(1)

    build_html(questions, args.out)

    json_out = args.out.replace(".html", ".json")
    Path(json_out).write_text(
        json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Also saved raw JSON → {json_out}")
    print("\nDone!")


if __name__ == "__main__":
    main()
