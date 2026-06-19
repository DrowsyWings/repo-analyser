import { useEffect, useState } from "react";
import GraphView from "./components/GraphView";
import api from "./services/api";
import { getLayoutedElements } from "./utils/layout";

function handleNodeClick(event, node) {
  console.log(node);
}

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  async function loadGraph() {
    const response = await api.get("/graph?path=.");
    const rfNodes = response.data.nodes.map((node, index) => ({
      id: node.id,
      position: {
        x: (index % 4) * 250,
        y: Math.floor(index / 4) * 150,
      },
      data: {
        label: node.label,
      },
    }));

    const rfEdges = response.data.edges.map((edge, index) => ({
      id: `e-${index}`,
      source: edge.source,
      target: edge.target,
    }));

    const layouted = getLayoutedElements(rfNodes, rfEdges);

    setNodes(layouted.nodes);
    setEdges(layouted.edges);
    console.log(rfNodes);
    console.log(rfEdges);
    console.log(response.data);
  }

  useEffect(() => {
    loadGraph();
  }, []);

  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <GraphView nodes={nodes} edges={edges} onNodeClick={handleNodeClick} />
    </div>
  );
}
