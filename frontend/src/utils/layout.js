import dagre from "dagre";

const NODE_WIDTH = 420;
const NODE_HEIGHT = 110;

export function getLayoutedElements(nodes, edges, direction = "LR") {
  const graph = new dagre.graphlib.Graph();

  graph.setDefaultEdgeLabel(() => ({}));

  graph.setGraph({
    rankdir: direction,

    // much tighter
    ranksep: 90,
    nodesep: 55,
    edgesep: 20,

    marginx: 40,
    marginy: 40,

    ranker: "network-simplex",
    align: "UL",
  });

  nodes.forEach((node) => {
    graph.setNode(node.id, {
      width: NODE_WIDTH,
      height: NODE_HEIGHT,
    });
  });

  edges.forEach((edge) => {
    graph.setEdge(edge.source, edge.target);
  });

  dagre.layout(graph);

  return {
    nodes: nodes.map((node) => {
      const pos = graph.node(node.id);

      return {
        ...node,
        position: {
          x: pos.x - NODE_WIDTH / 2,
          y: pos.y - NODE_HEIGHT / 2,
        },
      };
    }),
    edges,
  };
}