import os

from google import genai
from google.genai import types

from backend.config import EMBED_MODEL

BATCH_SIZE = 100

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


def _embed(texts: list[str], task_type: str) -> list[list[float]]:
    client = _get_client()
    vectors: list[list[float]] = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        response = client.models.embed_content(
            model=EMBED_MODEL,
            contents=batch,
            config=types.EmbedContentConfig(task_type=task_type),
        )
        vectors.extend(embedding.values for embedding in response.embeddings)
    return vectors


def embed_documents(texts: list[str]) -> list[list[float]]:
    """Embed source chunks for storage/retrieval."""
    if not texts:
        return []
    return _embed(texts, "RETRIEVAL_DOCUMENT")


def embed_query(text: str) -> list[float]:
    """Embed a single search query."""
    return _embed([text], "RETRIEVAL_QUERY")[0]
