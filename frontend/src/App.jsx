import { useEffect, useState } from "react";
import GraphView from "./components/GraphView";
import api from "./services/api";
import { getLayoutedElements } from "./utils/layout";
import Sidebar from "./components/Sidebar";

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  async function handleNodeClick(event, node) {
    const response = await api.get("/file", {
      params: {
        path: node.data.path,
      },
    });

    setSelectedFile(response.data);
  }

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
        path: node.path,
        loc: node.loc,
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
    <div style={{ display: "flex", width: "100vw", height: "100vh" }}>
      <div style={{ flex: 3 }}>
        <GraphView nodes={nodes} edges={edges} onNodeClick={handleNodeClick} />
      </div>
      <div
        style={{
          flex: 1,
          borderLeft: "1px solid #ccc",
          overflow: "auto",
          padding: "1rem",
        }}
      >
        <div
          style={{
            padding: "16px",
            textAlign: "left",
          }}
        >
          <Sidebar fileData={selectedFile} />
        </div>
      </div>
    </div>
  );
}
