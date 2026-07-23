from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent / "cache"

SUPPORTED_LANGUAGES = {
    ".py",
    ".cpp",
    ".js",
    ".ts",
}

SUMMARY_CACHE_DIR = CACHE_DIR / "summaries"

SUMMARY_CACHE_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "gemini-2.5-flash"
