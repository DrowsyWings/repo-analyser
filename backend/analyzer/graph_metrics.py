from itertools import islice

import networkx as nx

MAX_CYCLES = 20


def build_nx_graph(graph: dict) -> nx.DiGraph:
    """Build a directed graph (source imports target) from a graph dict."""
    g = nx.DiGraph()
    for node in graph["nodes"]:
        g.add_node(
            node["id"],
            label=node["label"],
            path=node["path"],
            loc=node["loc"],
        )
    for edge in graph["edges"]:
        g.add_edge(edge["source"], edge["target"])
    return g


def find_cycles(graph: dict, max_cycles: int = MAX_CYCLES) -> list[list[str]]:
    """Import cycles as lists of file labels (capped at max_cycles)."""
    g = build_nx_graph(graph)
    label_by_id = {n["id"]: n["label"] for n in graph["nodes"]}
    return [
        [label_by_id.get(node_id, node_id) for node_id in cycle]
        for cycle in islice(nx.simple_cycles(g), max_cycles)
    ]
