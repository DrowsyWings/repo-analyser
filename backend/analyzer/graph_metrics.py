from collections import Counter
from itertools import islice

import networkx as nx

MAX_CYCLES = 20
LOUVAIN_SEED = 42


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


def most_central(graph: dict, top_n: int = 5) -> list[dict]:
    """Most depended-on files ("read these first"), ranked by in-degree."""
    g = build_nx_graph(graph)
    if g.number_of_nodes() == 0:
        return []

    centrality = nx.in_degree_centrality(g)  # pure-python, no scipy
    in_degree = dict(g.in_degree())
    label_by_id = {n["id"]: n["label"] for n in graph["nodes"]}
    path_by_id = {n["id"]: n["path"] for n in graph["nodes"]}

    ordered = sorted(
        centrality,
        key=lambda nid: (in_degree.get(nid, 0), centrality[nid]),
        reverse=True,
    )[:top_n]
    return [
        {
            "name": label_by_id.get(node_id, node_id),
            "path": path_by_id.get(node_id, node_id),
            "score": round(centrality[node_id], 4),
            "in_degree": in_degree.get(node_id, 0),
        }
        for node_id in ordered
    ]


def _parent_name(path: str) -> str:
    parts = path.replace("\\", "/").split("/")
    return parts[-2] if len(parts) >= 2 else ""


def assign_communities(graph: dict, seed: int = LOUVAIN_SEED) -> dict[str, str]:
    """Map each node id to a community label (Louvain clustering)."""
    g = build_nx_graph(graph).to_undirected()
    if g.number_of_nodes() == 0:
        return {}

    path_by_id = {n["id"]: n["path"] for n in graph["nodes"]}
    communities = nx.community.louvain_communities(g, seed=seed)

    labels: dict[str, str] = {}
    used: Counter = Counter()
    for index, members in enumerate(communities):
        dirs = Counter(_parent_name(path_by_id.get(nid, "")) for nid in members)
        representative = dirs.most_common(1)[0][0] or f"module{index + 1}"
        used[representative] += 1
        label = (
            representative
            if used[representative] == 1
            else f"{representative} {used[representative]}"
        )
        for nid in members:
            labels[nid] = label
    return labels


def orphan_files(graph: dict) -> list[dict]:
    """Files with no inbound or outbound intra-repo edges (isolated)."""
    g = build_nx_graph(graph)
    label_by_id = {n["id"]: n["label"] for n in graph["nodes"]}
    path_by_id = {n["id"]: n["path"] for n in graph["nodes"]}
    return [
        {
            "name": label_by_id.get(node_id, node_id),
            "path": path_by_id.get(node_id, node_id),
        }
        for node_id in nx.isolates(g)
    ]
