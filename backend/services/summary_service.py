import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv("backend/.env")

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


def summarize(path: str):

    content = Path(path).read_text(encoding="utf-8")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{PROMPT}\n\n{content}",
    )

    return {"summary": response.text}
