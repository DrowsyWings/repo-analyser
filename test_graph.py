from backend.analyzer.graph_builder import build_graph

graph = build_graph(".")

print(graph)
print(f"Nodes: {graph['node_count']}")
print(f"Edges: {graph['edge_count']}")