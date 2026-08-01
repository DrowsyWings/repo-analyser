import os

from google import genai

from backend.analyzer.chunker import chunk_file
from backend.analyzer.scanner import scan_repo
from backend.config import MODEL
from backend.services import vector_store
from backend.services.embedding_service import embed_documents, embed_query
from backend.services.graph_service import get_graph

TOP_K = 5
MAX_NEIGHBOR_FILES = 5

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


CHAT_PROMPT = """You are a senior engineer helping a developer understand a codebase.
Answer the question using only the code context below. Reference the files you used.
If the context does not contain the answer, say so plainly.

Question:
{question}

Code context:
{context}
"""


def ensure_index(repo_path: str) -> None:
    if vector_store.has_index(repo_path):
        return
    chunks = []
    for file in scan_repo(repo_path):
        chunks.extend(chunk_file(file.path))
    if not chunks:
        return
    embeddings = embed_documents([c.content for c in chunks])
    vector_store.build_index(repo_path, chunks, embeddings)


def _neighbor_paths(repo_path: str, paths: list[str]) -> list[str]:
    """Import-graph neighbors (imports + imported-by) of the given files."""
    graph = get_graph(repo_path)
    id_by_path = {n["path"]: n["id"] for n in graph["nodes"]}
    path_by_id = {n["id"]: n["path"] for n in graph["nodes"]}

    adjacency: dict[str, set] = {}
    for edge in graph["edges"]:
        adjacency.setdefault(edge["source"], set()).add(edge["target"])
        adjacency.setdefault(edge["target"], set()).add(edge["source"])

    seen = set(paths)
    neighbors: list[str] = []
    for path in paths:
        node_id = id_by_path.get(path)
        if node_id is None:
            continue
        for neighbor_id in adjacency.get(node_id, ()):
            neighbor_path = path_by_id.get(neighbor_id)
            if neighbor_path and neighbor_path not in seen:
                seen.add(neighbor_path)
                neighbors.append(neighbor_path)
                if len(neighbors) >= MAX_NEIGHBOR_FILES:
                    return neighbors
    return neighbors


def _one_chunk_per_file(chunks: list[dict]) -> list[dict]:
    picked: dict[str, dict] = {}
    for chunk in chunks:
        path = chunk["metadata"]["path"]
        picked.setdefault(path, chunk)
    return list(picked.values())


def retrieve(repo_path: str, question: str, k: int = TOP_K) -> list[dict]:
    hits = vector_store.query(repo_path, embed_query(question), k=k)

    hit_paths = [hit["metadata"]["path"] for hit in hits]
    neighbor_paths = _neighbor_paths(repo_path, hit_paths)
    if neighbor_paths:
        neighbors = vector_store.get_file_chunks(repo_path, neighbor_paths)
        hits.extend(_one_chunk_per_file(neighbors))

    return hits


def _format_context(hits: list[dict]) -> str:
    blocks = []
    for hit in hits:
        meta = hit["metadata"]
        blocks.append(
            f"# {meta['path']} — {meta['name']} "
            f"(lines {meta['start_line']}-{meta['end_line']})\n{hit['content']}"
        )
    return "\n\n".join(blocks)


def _citations(hits: list[dict]) -> list[dict]:
    seen = set()
    citations = []
    for hit in hits:
        meta = hit["metadata"]
        key = (meta["path"], meta["start_line"], meta["end_line"])
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            {
                "path": meta["path"],
                "name": meta["name"],
                "start_line": meta["start_line"],
                "end_line": meta["end_line"],
            }
        )
    return citations


def answer_question(repo_path: str, question: str, k: int = TOP_K) -> dict:
    ensure_index(repo_path)
    if not vector_store.has_index(repo_path):
        return {
            "answer": "No analysable source files were found in this repository.",
            "citations": [],
        }

    hits = retrieve(repo_path, question, k=k)
    prompt = CHAT_PROMPT.format(question=question, context=_format_context(hits))
    response = _get_client().models.generate_content(model=MODEL, contents=prompt)
    return {"answer": response.text, "citations": _citations(hits)}


def stream_answer(repo_path: str, question: str, k: int = TOP_K):
    """Yield {"type": "token"|"done", ...} events for an SSE chat response."""
    ensure_index(repo_path)
    if not vector_store.has_index(repo_path):
        yield {
            "type": "token",
            "text": "No analysable source files were found in this repository.",
        }
        yield {"type": "done", "citations": []}
        return

    hits = retrieve(repo_path, question, k=k)
    prompt = CHAT_PROMPT.format(question=question, context=_format_context(hits))

    stream = _get_client().models.generate_content_stream(model=MODEL, contents=prompt)
    for chunk in stream:
        if chunk.text:
            yield {"type": "token", "text": chunk.text}

    yield {"type": "done", "citations": _citations(hits)}
