from backend.analyzer.graph_builder import build_graph

_graph_cache = {}


def get_graph(repo_path: str):
    if repo_path not in _graph_cache:
        _graph_cache[repo_path] = build_graph(repo_path)

    return _graph_cache[repo_path]


def clear_graph_cache():
    _graph_cache.clear()
