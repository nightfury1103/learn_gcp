#!/usr/bin/env python3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = (ROOT / "index.html").read_text()
SW = (ROOT / "sw.js").read_text()


def require(text, needle, label):
    if needle not in text:
        raise SystemExit(f"missing {label}: {needle}")


def main():
    require(INDEX, "GitHub storage", "storage panel title")
    require(INDEX, "id=\"githubToken\"", "token input")
    require(INDEX, "id=\"gistId\"", "gist id input")
    require(INDEX, "pca-github-sync-v1", "sync settings key")
    require(INDEX, "function saveProgressToGitHub", "github save function")
    require(INDEX, "function loadProgressFromGitHub", "github load function")
    require(INDEX, "function scheduleGitHubSave", "debounced auto save")
    require(INDEX, "function connectGitHubStorage", "connect storage function")
    require(INDEX, "save({sync:true})", "attempt autosync")
    require(INDEX, "setState(item.id,{known:!state(item.id).known},{sync:true})", "known autosync")
    require(INDEX, "setState(item.id,{missed:!state(item.id).missed},{sync:true})", "missed autosync")
    require(INDEX, "window.onload=()=>{draw();loadGitHubSettings();loadProgressFromGitHub();};", "github progress autoload")
    require(INDEX, "GitHub is the saved progress store", "storage source of truth hint")
    require(SW, 'const CACHE_NAME = "gcp-pca-study-v11";', "service worker cache bump")
    print("static sync checks passed")


if __name__ == "__main__":
    main()
