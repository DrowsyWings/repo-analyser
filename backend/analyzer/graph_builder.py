from pathlib import Path

from backend.analyzer.parser import (
    extract_python_imports,
    get_loc,
)
from backend.analyzer.scanner import scan_repo


def build_nodes(files):
    nodes = []

    for file in files:
        nodes.append(
            {
                "id": str(file.module_name),
                "label": file.name,
                "path": file.path,
                "loc": get_loc(file.path),
            }
        )

    return nodes


def build_module_lookup(files):
    lookup = {}

    for file in files:
        # path = Path(file.path)
        # lookup[path.stem] = file.path
        lookup[file.module_name] = file
    return lookup


def build_edges(files):
    edges = []

    module_lookup = build_module_lookup(files)

    for file in files:
        if file.extension != ".py":
            continue

        imports = extract_python_imports(file.path)

        for imp in imports:
            if imp not in module_lookup:
                continue

            target_file = module_lookup[imp]

            edges.append(
                {
                    "source": file.module_name,
                    "target": target_file.module_name,
                }
            )

    return edges


def build_graph(repo_path):
    files = scan_repo(repo_path)

    nodes = build_nodes(files)
    edges = build_edges(files)

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


_graph_cache = None


def get_graph(repo_path):
    global _graph_cache

    if _graph_cache is None:
        _graph_cache = build_graph(repo_path)

    return _graph_cache


def build_reverse_lookup(edges):
    reverse = {}

    for edge in edges:
        target = edge["target"]
        source = edge["source"]

        if target not in reverse:
            reverse[target] = []

        reverse[target].append(source)

    return reverse
