#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


SITE = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = SITE / "pde_questions_crawled.json"
DEFAULT_TEMPLATE = SITE / "pca.html"
DEFAULT_OVERRIDES = SITE / "pde_keyword_overrides.json"



def norm(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(value)).lower()).strip()


def cue_parts(cue: str) -> list[str]:
    return [part.strip() for part in str(cue).split("+") if part.strip()]


def validate_cue(row: dict) -> None:
    text = norm(row["questionText"])
    missing = [part for part in cue_parts(row["cue"]) if norm(part) not in text]
    if missing:
        raise ValueError(f"{row['ref']} cue parts not in question: {missing}")


def make_cue(question_text: str) -> str:
    """Fallback when no curated override exists. Never use a long stem as a keyword."""
    return ""


def make_cue_why(row: dict) -> str:
    trigger = row["cue"] or ""
    answer = row["answerPattern"]
    if len(answer) > 220:
        answer = answer[:217].rstrip() + "..."
    if not trigger:
        return (
            "Keyword not curated yet for this question. "
            f"Correct answer {row['answerLetters']}: {answer}"
        )
    return (
        f"When you see '{trigger}' in the question, map it to answer "
        f"{row['answerLetters']}: {answer}"
    )


def load_keyword_overrides(path: Path) -> dict[tuple[int, int], dict]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[tuple[int, int], dict] = {}
    for key, value in raw.items():
        topic_s, q_s = str(key).split("-", 1)
        out[(int(topic_s), int(q_s))] = value
    return out


def convert_source_row(
    row: dict,
    next_id: int,
    overrides: dict[tuple[int, int], dict] | None = None,
) -> dict:
    question_number = row["question_number"]
    topic = row["topic"]
    year = row.get("year")
    question_text = row["question_text"]
    answer_letters = row.get("suggested_answer", "")
    options = row.get("options", [])
    answers = set(answer_letters)
    selected = [
        f"{o.get('label')}: {o.get('text')}"
        for o in options
        if o.get("label") in answers
    ]
    override = (overrides or {}).get((topic, question_number), {})
    result = {
        "id": next_id,
        "year": year,
        "topic": topic,
        "questionNumber": question_number,
        "ref": (
            f"{year} / T{topic} Q{question_number}"
            if year is not None
            else f"T{topic} Q{question_number}"
        ),
        "cue": override.get("cue") or make_cue(question_text),
        "category": "General",
        "answerLetters": answer_letters,
        "answerPattern": " | ".join(selected),
        "questionText": question_text,
        "options": options,
        "url": row.get("url", ""),
        "isNew": False,
        "sourceType": "Dump",
        "caseStudy": "",
        "sortOrder": int(year or 0) * 10000 + topic * 1000 + question_number,
    }
    result["cueWhy"] = override.get("cueWhy") or make_cue_why(result)
    validate_cue(result)
    return result


def build_data(
    source: Path,
    min_year: int | None = None,
    overrides: dict[tuple[int, int], dict] | None = None,
) -> list[dict]:
    source_rows = json.loads(source.read_text(encoding="utf-8"))
    if min_year is not None:
        source_rows = [
            row
            for row in source_rows
            if isinstance(row.get("year"), int) and row["year"] >= min_year
        ]
    rows = [
        convert_source_row(source_row, idx, overrides=overrides)
        for idx, source_row in enumerate(source_rows, 1)
    ]
    rows.sort(
        key=lambda row: (
            row["year"] if isinstance(row["year"], int) else 0,
            row["topic"],
            row["questionNumber"],
        )
    )
    for idx, row in enumerate(rows, 1):
        row["id"] = idx
    return rows


def make_reference(rows: list[dict], min_year: int | None = None) -> str:
    scope = (
        f"Professional Data Engineer dump ({min_year}+)"
        if min_year is not None
        else "Professional Data Engineer dump"
    )
    lines = [
        "# GCP Professional Data Engineer Study Set",
        "",
        "This set contains real crawled ExamTopics Professional Data Engineer questions"
        + (f" from {min_year} to now." if min_year is not None else ".")
        + " No generated questions are included.",
        "",
        "| Group | Questions |",
        "|---|---:|",
        f"| {scope} | {len(rows)} |",
        "",
        "## Questions",
        "",
        "| Ref | Keyword | Why keyword | Answer |",
        "|---|---|---|---|",
    ]
    for row in sorted(rows, key=lambda item: (item["sortOrder"], item["questionNumber"])):
        lines.append(
            f"| {row['ref']} | {row['cue']} | {row['cueWhy']} | {row['answerLetters']} |"
        )
    return "\n".join(lines) + "\n"


def strip_pca_case_filters(text: str) -> str:
    """Remove PCA case-study filter chrome that does not apply to PDE dumps."""
    # Primary mode seg: drop Non-case / Cases / New (PCA case + upload flags).
    text = text.replace(
        '<button data-mode="noncase" onclick="setMode(\'noncase\',this)">Non-case</button>',
        "",
    )
    text = text.replace(
        '<button data-mode="case" onclick="setMode(\'case\',this)">Cases</button>',
        "",
    )
    text = text.replace(
        '<button data-mode="new" onclick="setMode(\'new\',this)">New</button>',
        "",
    )
    # Second seg: named PCA case studies.
    text = re.sub(
        r'<div class="seg"><button data-mode="case:Altostrat Media".*?</div>',
        "",
        text,
        count=1,
    )
    # Side panel listing PCA case-study counts.
    text = re.sub(
        r'<div class="panel"><h2>Real case-study count</h2><div id="caseCounts" class="caseCounts"></div></div>',
        "",
        text,
        count=1,
    )
    # Replace entire PCA case-count renderer with a safe no-op.
    text = re.sub(
        r"function renderCaseCounts\(\)\{.*?\}(?=function )",
        "function renderCaseCounts(){if($('caseCounts'))$('caseCounts').innerHTML='';}",
        text,
        count=1,
        flags=re.S,
    )
    return text


def render_study_page(
    rows: list[dict],
    *,
    template_path: Path,
    out_path: Path,
    title: str,
    subtitle: str,
    store_key: str,
) -> None:
    text = template_path.read_text(encoding="utf-8")
    data_json = json.dumps(rows, ensure_ascii=True)

    text = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", text)
    text = re.sub(r"(<div class=\"title\"><h1>)(.*?)(</h1>)", rf"\1{title}\3", text)
    text = re.sub(
        rf"(<div class=\"title\"><h1>{re.escape(title)}</h1><p>)(.*?)(</p>)",
        rf"\1{subtitle}\3",
        text,
        count=1,
    )
    text = re.sub(
        r'(<strong id="totalCount">)\d+(</strong>)',
        rf"\g<1>{len(rows)}\2",
        text,
    )
    text = re.sub(
        r'(<strong id="matchCount">)\d+(</strong>)',
        rf"\g<1>{len(rows)}\2",
        text,
    )
    text = re.sub(r"const storeKey='[^']+'", f"const storeKey='{store_key}'", text)
    text = re.sub(
        r"const DATA = \[.*?\];let mode",
        lambda _: f"const DATA = {data_json};let mode",
        text,
        flags=re.S,
    )
    if "keywordWhy" not in text:
        text = text.replace(
            '<div class="label">Exact keyword</div><div id="correctKeyword" class="value cueValue"></div><div class="label">Answer pattern</div>',
            '<div class="label">Exact keyword</div><div id="correctKeyword" class="value cueValue"></div><div class="label">Why keyword</div><div id="keywordWhy" class="value"></div><div class="label">Answer pattern</div>',
        )
        text = text.replace(
            "$('correctKeyword').textContent=item.cue;$('answerPattern').textContent=item.answerPattern;",
            "$('correctKeyword').textContent=item.cue;$('keywordWhy').textContent=item.cueWhy;$('answerPattern').textContent=item.answerPattern;",
        )
    text = text.replace('href="full-real-study-reference.md"', 'href="pde-study-reference.md"')
    text = text.replace('href="real-dump-study-reference.md"', 'href="pde-study-reference.md"')
    text = strip_pca_case_filters(text)
    if 'href="index.html"' not in text.split("const DATA")[0]:
        text = text.replace(
            '<div class="title">',
            '<div class="title"><a href="index.html" style="display:inline-block;margin-bottom:6px;color:#0f8a5f;font-size:12px;font-weight:700;text-decoration:none">← All certs</a>',
            1,
        )
    text = inject_keyword_popup(text)
    out_path.write_text(text, encoding="utf-8")


def inject_keyword_popup(text: str) -> str:
    """No popup. Keep inline reveal; only highlight short curated cues."""
    text = re.sub(
        r'<div id="keywordModal" class="keywordModal".*?</div></div>',
        "",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"\.keywordModal\{.*?\.keywordModalCard button\{[^}]*\}",
        "",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"function openKeywordModal\(item,answerOk\)\{.*?function closeKeywordModal\(\)\{.*?\}",
        "",
        text,
        count=1,
        flags=re.S,
    )
    text = text.replace("openKeywordModal(item,answerOk);", "")

    # Prefer a surgical edit of the original highlight() — do not rewrite the regex.
    text = text.replace(
        ".map(x=>x.trim()).filter(Boolean).sort((a,b)=>b.length-a.length);",
        ".map(x=>x.trim()).filter(Boolean).filter(p=>p.length>0&&p.length<=80)"
        ".sort((a,b)=>b.length-a.length);",
        1,
    )
    text = text.replace(
        "const parts=String(phrase).split('+')",
        "const parts=String(phrase||'').split('+')",
        1,
    )

    # Refresh inline reveal fields on Check; highlight only when cue is short.
    replacements = [
        (
            "$('questionText').innerHTML=highlight(item.questionText,item.cue,true);"
            "$('matchResult').textContent=`${answerOk?'Answer OK':'Answer missed'} - keyword is now highlighted in the question`;"
            "$('reveal').className='reveal show';$('showBtn').textContent='Next';recordAttempt(item,picked,answerOk);",
            (
                "$('matchResult').textContent=answerOk?'Answer OK':'Answer missed';"
                "$('correctKeyword').textContent=item.cue||'(not curated yet)';"
                "$('keywordWhy').textContent=item.cueWhy||'';"
                "$('answerPattern').textContent=item.answerPattern||'';"
                "$('questionText').innerHTML=highlight(item.questionText,item.cue,!!(item.cue&&item.cue.length<=80));"
                "$('reveal').className='reveal show';$('showBtn').textContent='Next';"
                "recordAttempt(item,picked,answerOk);"
            ),
        ),
        (
            "$('questionText').innerHTML=highlight(item.questionText,item.cue,true);"
            "$('matchResult').textContent=answerOk?'Answer OK':'Answer missed';",
            (
                "$('matchResult').textContent=answerOk?'Answer OK':'Answer missed';"
                "$('correctKeyword').textContent=item.cue||'(not curated yet)';"
                "$('keywordWhy').textContent=item.cueWhy||'';"
                "$('answerPattern').textContent=item.answerPattern||'';"
                "$('questionText').innerHTML=highlight(item.questionText,item.cue,!!(item.cue&&item.cue.length<=80));"
            ),
        ),
    ]
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new, 1)
            break
    return text


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build PDE study page from crawled JSON without overwriting PCA index."
    )
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    ap.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    ap.add_argument("--min-year", type=int, default=2024)
    ap.add_argument("--out-html", type=Path, default=SITE / "pde.html")
    ap.add_argument("--out-data", type=Path, default=SITE / "pde-study-data.json")
    ap.add_argument("--out-reference", type=Path, default=SITE / "pde-study-reference.md")
    args = ap.parse_args()

    if not args.source.exists():
        raise SystemExit(f"Source JSON not found: {args.source}")
    if not args.template.exists():
        raise SystemExit(f"Template HTML not found: {args.template}")

    overrides = load_keyword_overrides(args.overrides)
    rows = build_data(args.source, min_year=args.min_year, overrides=overrides)
    if not rows:
        raise SystemExit(
            f"No questions with year >= {args.min_year}. "
            "Refresh years on the source JSON first."
        )

    args.out_data.write_text(
        json.dumps(rows, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    args.out_reference.write_text(
        make_reference(rows, min_year=args.min_year), encoding="utf-8"
    )
    render_study_page(
        rows,
        template_path=args.template,
        out_path=args.out_html,
        title="GCP PDE Study (2024–Now)",
        subtitle=(
            f"Real ExamTopics Professional Data Engineer dump questions from "
            f"{args.min_year} to now ({len(rows)} questions). No generated questions."
        ),
        store_key="pde-2024-now-study-v1",
    )
    curated = sum(
        1
        for row in rows
        if (row["topic"], row["questionNumber"]) in overrides
    )
    print(
        json.dumps(
            {
                "total": len(rows),
                "min_year": args.min_year,
                "curated_keywords": curated,
                "source": str(args.source),
                "html": str(args.out_html),
                "data": str(args.out_data),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
