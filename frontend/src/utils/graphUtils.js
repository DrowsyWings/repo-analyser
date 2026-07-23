export function buildAdjacency(edges) {
  const outgoing = new Map();
  const incoming = new Map();

  for (const edge of edges) {
    if (!outgoing.has(edge.source)) outgoing.set(edge.source, []);
    if (!incoming.has(edge.target)) incoming.set(edge.target, []);

    outgoing.get(edge.source).push(edge.target);
    incoming.get(edge.target).push(edge.source);
  }

  return { outgoing, incoming };
}

export function getNeighborhood(start, adjacency, hops = 1) {
  const visible = new Set([start]);

  let frontier = [start];

  for (let h = 0; h < hops; h++) {
    const next = [];

    for (const node of frontier) {
      const out = adjacency.outgoing.get(node) || [];
      const inc = adjacency.incoming.get(node) || [];

      for (const x of [...out, ...inc]) {
        if (!visible.has(x)) {
          visible.add(x);
          next.push(x);
        }
      }
    }

    frontier = next;
  }

  return visible;
}

export function highlightGraph(nodes, edges, selected) {
  const connected = new Set();

  edges.forEach((e) => {
    if (e.source === selected || e.target === selected) {
      connected.add(e.source);
      connected.add(e.target);
    }
  });

  const newNodes = nodes.map((n) => ({
    ...n,
    data: {
      ...n.data,
      state:
        n.id === selected
          ? "selected"
          : connected.has(n.id)
            ? "neighbor"
            : "dim",
    },
  }));

  const newEdges = edges.map((e) => ({
    ...e,
    animated: e.source === selected || e.target === selected,
    style: {
      stroke:
        e.source === selected || e.target === selected
          ? "var(--accent)"
          : "#cbd5e1",
      strokeWidth: e.source === selected || e.target === selected ? 2.6 : 1.3,
      opacity: e.source === selected || e.target === selected ? 1 : 0.55,
    },
  }));

  return {
    nodes: newNodes,
    edges: newEdges,
  };
}
