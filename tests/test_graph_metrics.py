from backend.analyzer.graph_metrics import (
    build_nx_graph,
    find_cycles,
    most_central,
    orphan_files,
)

GRAPH = {
    "nodes": [
        {"id": "a", "label": "a.py", "path": "a.py", "loc": 5},
        {"id": "b", "label": "b.py", "path": "b.py", "loc": 3},
        {"id": "c", "label": "c.py", "path": "c.py", "loc": 8},
    ],
    "edges": [
        {"source": "a", "target": "b"},
        {"source": "b", "target": "c"},
    ],
}


def test_build_nx_graph_preserves_nodes_edges_and_attrs():
    g = build_nx_graph(GRAPH)

    assert g.number_of_nodes() == 3
    assert g.number_of_edges() == 2
    assert g.has_edge("a", "b")
    assert not g.has_edge("b", "a")  # directed
    assert g.nodes["a"]["label"] == "a.py"
    assert g.nodes["c"]["loc"] == 8


def test_find_cycles_none_when_acyclic():
    assert find_cycles(GRAPH) == []


def test_find_cycles_detects_cycle_with_labels():
    cyclic = {
        "nodes": [
            {"id": "a", "label": "a.py", "path": "a.py", "loc": 1},
            {"id": "b", "label": "b.py", "path": "b.py", "loc": 1},
        ],
        "edges": [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "a"},
        ],
    }
    cycles = find_cycles(cyclic)
    assert len(cycles) == 1
    assert set(cycles[0]) == {"a.py", "b.py"}  # labels, not ids


def test_find_cycles_respects_cap():
    # two independent 2-cycles; cap to 1
    graph = {
        "nodes": [
            {"id": c, "label": f"{c}.py", "path": f"{c}.py", "loc": 1} for c in "abcd"
        ],
        "edges": [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "a"},
            {"source": "c", "target": "d"},
            {"source": "d", "target": "c"},
        ],
    }
    assert len(find_cycles(graph, max_cycles=1)) == 1


def test_most_central_ranks_most_imported_first():
    # b and c both import a -> a is the most depended-on
    graph = {
        "nodes": [
            {"id": "a", "label": "a.py", "path": "a.py", "loc": 1},
            {"id": "b", "label": "b.py", "path": "b.py", "loc": 1},
            {"id": "c", "label": "c.py", "path": "c.py", "loc": 1},
        ],
        "edges": [
            {"source": "b", "target": "a"},
            {"source": "c", "target": "a"},
        ],
    }
    central = most_central(graph, top_n=1)
    assert central[0]["name"] == "a.py"
    assert central[0]["in_degree"] == 2


def test_most_central_empty_graph():
    assert most_central({"nodes": [], "edges": []}) == []


def test_orphan_files_finds_isolated_nodes():
    graph = {
        "nodes": [
            {"id": "a", "label": "a.py", "path": "a.py", "loc": 1},
            {"id": "b", "label": "b.py", "path": "b.py", "loc": 1},
            {"id": "lonely", "label": "lonely.py", "path": "lonely.py", "loc": 1},
        ],
        "edges": [{"source": "a", "target": "b"}],
    }
    orphans = orphan_files(graph)
    assert [o["name"] for o in orphans] == ["lonely.py"]
