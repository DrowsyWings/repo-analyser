from collections import Counter
from pathlib import Path

from backend.analyzer.graph_builder import build_graph

_graph_cache: dict = {}


def get_graph(repo_path: str):
    if repo_path not in _graph_cache:
        _graph_cache[repo_path] = build_graph(repo_path)
    return _graph_cache[repo_path]


def clear_graph_cache():
    _graph_cache.clear()


def get_stats(repo_path: str):
    graph = get_graph(repo_path)
    nodes = graph["nodes"]

    if not nodes:
        return {
            "total_files": 0,
            "total_loc": 0,
            "average_loc": 0,
            "languages": {},
            "largest_files": [],
        }

    total_loc = sum(n["loc"] for n in nodes)
    average_loc = round(total_loc / len(nodes), 1)

    lang_counts: Counter = Counter()
    for node in nodes:
        ext = Path(node["path"]).suffix
        if ext:
            lang_counts[ext] += 1

    largest = sorted(nodes, key=lambda n: n["loc"], reverse=True)[:5]

    return {
        "total_files": len(nodes),
        "total_loc": total_loc,
        "average_loc": average_loc,
        "languages": dict(lang_counts),
        "largest_files": [
            {"name": n["label"], "loc": n["loc"], "path": n["path"]}
            for n in largest
        ],
    }