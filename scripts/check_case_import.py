#!/usr/bin/env python3
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "full-real-study-data.json").read_text())
INDEX = (ROOT / "index.html").read_text()
SW = (ROOT / "sw.js").read_text()


def require(condition, message):
    if not condition:
        raise SystemExit(message)


counts = Counter(row.get("caseStudy") or "Non-case" for row in DATA)

require(len(DATA) == 180, f"expected 180 study rows, found {len(DATA)}")
require(counts["Altostrat Media"] == 33, counts)
require(counts["Cymbal Retail"] == 27, counts)
require(counts["EHR Healthcare"] == 29, counts)
require(counts["KnightMotives Automotive"] == 25, counts)
require(counts["Non-case"] == 66, counts)

texts = [row["questionText"].strip().lower() for row in DATA]
require(len(texts) == len(set(texts)), "duplicate question text exists")

uploaded = [row for row in DATA if row.get("sourceType") == "Uploaded case JSON"]
require(len(uploaded) == 89, f"expected 89 uploaded case JSON rows, found {len(uploaded)}")
require(all(row["caseStudy"] in counts for row in uploaded), "uploaded row missing case study")
require(all(row["cue"].startswith(row["caseStudy"] + " + ") for row in uploaded), "uploaded cue missing case name")
require(all(row.get("cueWhy") and row["cueWhy"] != row["cue"] for row in uploaded), "uploaded row missing explanation")
require(all(row.get("answerPattern") for row in uploaded), "uploaded row missing answer pattern")

for marker in ["GCP PCA Full Case Study", "Uploaded case-study JSON", "180"]:
    require(marker in INDEX, f"index missing marker {marker}")

require('const CACHE_NAME = "gcp-pca-study-v11";' in SW, "service worker cache was not bumped to v11")

print("case import checks passed")
