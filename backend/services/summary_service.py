import json
import os
from datetime import datetime
from hashlib import sha256
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from backend.config import MODEL, SUMMARY_CACHE_DIR

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT = """
You are a senior software engineer.

Explain this source file for a new developer joining the project.

Return markdown.

Include:

## Purpose

## Responsibilities

## Main Classes / Functions

## Dependencies

## Notes

Maximum 150 words.

Do not explain every line.
"""


def compute_hash(content: str):
    return sha256(content.encode("utf-8")).hexdigest()


def load_cached_summary(hash_value: str):

    cache_file = SUMMARY_CACHE_DIR / f"{hash_value}.json"

    if not cache_file.exists():
        return None

    print(f"[CACHE HIT] {hash_value}")

    with open(cache_file, "r") as f:
        return json.load(f)


def save_cached_summary(
    hash_value: str,
    summary: str | None,
):

    cache_file = SUMMARY_CACHE_DIR / f"{hash_value}.json"

    data = {
        "summary": summary,
        "generated_at": datetime.now().isoformat(),
        "model": MODEL,
    }

    with open(cache_file, "w") as f:
        json.dump(data, f, indent=4)


def summarize(path: str):

    content = Path(path).read_text(encoding="utf-8")

    hash_value = compute_hash(content)

    cached = load_cached_summary(hash_value)

    if cached:
        return cached

    print(f"[CACHE MISS] {hash_value}")

    response = client.models.generate_content(
        model=MODEL,
        contents=f"{PROMPT}\n\n{content}",
    )

    summary = response.text

    save_cached_summary(hash_value, summary)

    return {
        "summary": summary,
        "generated_at": datetime.now().isoformat(),
        "model": MODEL,
    }
