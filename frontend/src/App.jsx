import { useEffect, useState } from "react";
import GraphView from "./components/GraphView";
import api from "./services/api";

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  
  async function loadGraph() {
    const response = await api.get("/graph");

    console.log(response.data);
  }

  useEffect(() => {
    loadGraph();
  }, []);

  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <GraphView nodes={nodes} edges={edges} />
    </div>
  );
}