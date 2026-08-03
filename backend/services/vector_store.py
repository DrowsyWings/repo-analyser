import hashlib

import chromadb
from chromadb.config import Settings

from backend.analyzer.chunker import Chunk
from backend.config import CACHE_DIR

CHROMA_DIR = CACHE_DIR / "chroma"

_client = None


def _get_client():
    global _client
    if _client is None:
        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
    return _client


def _collection_name(repo_id: str) -> str:
    digest = hashlib.sha256(repo_id.encode()).hexdigest()[:32]
    return f"repo_{digest}"


def has_index(repo_id: str) -> bool:
    client = _get_client()
    try:
        collection = client.get_collection(_collection_name(repo_id))
    except Exception:
        return False
    return collection.count() > 0


def build_index(
    repo_id: str, chunks: list[Chunk], embeddings: list[list[float]]
) -> None:
    client = _get_client()
    name = _collection_name(repo_id)

    try:
        client.delete_collection(name)
    except Exception:
        pass

    collection = client.create_collection(name)
    collection.add(
        ids=[str(i) for i in range(len(chunks))],
        embeddings=embeddings,
        documents=[c.content for c in chunks],
        metadatas=[
            {
                "path": c.path,
                "name": c.name,
                "kind": c.kind,
                "start_line": c.start_line,
                "end_line": c.end_line,
            }
            for c in chunks
        ],
    )


def query(repo_id: str, query_embedding: list[float], k: int = 5) -> list[dict]:
    client = _get_client()
    collection = client.get_collection(_collection_name(repo_id))
    result = collection.query(query_embeddings=[query_embedding], n_results=k)

    hits = []
    for document, metadata, distance in zip(
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        hits.append({"content": document, "metadata": metadata, "distance": distance})
    return hits


def get_file_chunks(repo_id: str, paths: list[str]) -> list[dict]:
    if not paths:
        return []
    client = _get_client()
    try:
        collection = client.get_collection(_collection_name(repo_id))
    except Exception:
        return []

    result = collection.get(where={"path": {"$in": list(paths)}})
    return [
        {"content": document, "metadata": metadata, "distance": None}
        for document, metadata in zip(result["documents"], result["metadatas"])
    ]
