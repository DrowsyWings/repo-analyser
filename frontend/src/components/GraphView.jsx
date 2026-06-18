import ReactFlow, {
  Background,
  Controls,
  MiniMap,
} from "reactflow";

import "reactflow/dist/style.css";

export default function GraphView({
  nodes,
  edges,
}) {
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      fitView
      nodesDraggable={true}
      elementsSelectable={true}

    >
      <Background />
      <Controls />
      <MiniMap />
    </ReactFlow>
  );
}