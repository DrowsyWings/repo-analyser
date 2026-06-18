// import ReactFlow from "reactflow";
import GraphView from "./components/GraphView";
import "reactflow/dist/style.css";

const nodes = [
  {
    id: "1",
    position: { x: 0, y: 0 },
    data: { label: "scanner.py" },
  },
  {
    id: "2",
    position: { x: 300, y: 0 },
    data: { label: "parser.py" },
  },
  {
    id: "3",
    position: { x: 150, y: 200 },
    data: { label: "graph_builder.py" },
  },
];

const edges = [
  {
    id: "e1",
    source: "3",
    target: "1",
  },
  {
    id: "e2",
    source: "3",
    target: "2",
  },
];

export default function App() {
  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
      }}
    >
      <GraphView
        nodes={nodes}
        edges={edges}
      />
    </div>
  );
}