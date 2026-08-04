from collections import Counter
from pathlib import Path

from backend.analyzer.graph_builder import build_graph
from backend.analyzer.graph_metrics import (
    assign_communities,
    find_cycles,
    most_central,
    orphan_files,
)

_graph_cache: dict = {}


def get_graph(repo_path: str):
    if repo_path not in _graph_cache:
        graph = build_graph(repo_path)
        communities = assign_communities(graph)
        for node in graph["nodes"]:
            node["community"] = communities.get(node["id"], "")
        _graph_cache[repo_path] = graph
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
            "cycles": [],
            "central_files": [],
            "orphan_files": [],
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
            {"name": n["label"], "loc": n["loc"], "path": n["path"]} for n in largest
        ],
        "cycles": find_cycles(graph),
        "central_files": most_central(graph),
        "orphan_files": orphan_files(graph),
    }
