import { useEffect } from "react";
import ReactFlow, {
  useNodesState,
  useEdgesState,
  Background,
  Controls,
  MiniMap,
} from "reactflow";
import "reactflow/dist/style.css";

export default function GraphView({ nodes, edges, onNodeClick }) {
  const [rfNodes, setNodes, onNodesChange] = useNodesState(nodes);

  const [rfEdges, setEdges, onEdgesChange] = useEdgesState(edges);

  useEffect(() => {
    setNodes(nodes);
  }, [nodes]);

  useEffect(() => {
    setEdges(edges);
  }, [edges]);

  return (
    <ReactFlow
      nodes={rfNodes}
      edges={rfEdges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
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
