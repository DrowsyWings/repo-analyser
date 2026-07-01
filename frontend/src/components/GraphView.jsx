import { forwardRef, useEffect, useImperativeHandle } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from "reactflow";
import "reactflow/dist/style.css";
import { toPng } from "html-to-image";
import CustomNode from "./CustomNode";

const nodeTypes = { customNode: CustomNode };

const LANG_COLORS = {
  ".py":  "#3776ab",
  ".js":  "#c8a428",
  ".ts":  "#3178c6",
  ".jsx": "#61dafb",
  ".tsx": "#61dafb",
  ".cpp": "#9560b0",
  ".c":   "#7cacbf",
  ".h":   "#7cacbf",
  ".hpp": "#9560b0",
};

const GraphViewInner = forwardRef(({ nodes, edges, onNodeClick }, ref) => {
  const [rfNodes, setNodes, onNodesChange] = useNodesState(nodes);
  const [rfEdges, setEdges, onEdgesChange] = useEdgesState(edges);
  const { setCenter, getNode, fitView } = useReactFlow();

  useEffect(() => { setNodes(nodes); }, [nodes]);
  useEffect(() => { setEdges(edges); }, [edges]);
  useEffect(() => {
    if (nodes.length > 0) {
      setTimeout(() => fitView({ padding: 0.15, duration: 400 }), 50);
    }
  }, []);

  useImperativeHandle(ref, () => ({
    focusNode: (nodeId) => {
      const node = getNode(nodeId);
      if (node) {
        setCenter(
          node.position.x + 100,
          node.position.y + 35,
          { zoom: 1.8, duration: 700 }
        );
      }
    },
    exportPNG: async () => {
      const el = document.querySelector(".react-flow");
      if (!el) return;
      try {
        const dataUrl = await toPng(el, { backgroundColor: "#1e1e1e" });
        const link = document.createElement("a");
        link.href = dataUrl;
        link.download = "repo-graph.png";
        link.click();
      } catch (e) {
        console.error("Export failed:", e);
      }
    },
  }));

  return (
    <ReactFlow
      nodes={rfNodes}
      edges={rfEdges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
      nodeTypes={nodeTypes}
      nodesDraggable
      elementsSelectable
      defaultEdgeOptions={{
        type: "smoothstep",
        style: { stroke: "#94a3b8", strokeWidth: 1.6 },
      }}
      fitView
    >
      <Background color="#d8e2ee" gap={26} size={1} />
      <Controls />
      <MiniMap
        nodeColor={(n) => {
          const ext = n.data?.path ? "." + n.data.path.split(".").pop() : "";
          return LANG_COLORS[ext] || "#555";
        }}
        maskColor="rgba(30,30,30,0.6)"
        style={{
          background: "#252526",
          border: "1px solid #3e3e42",
          borderRadius: "6px",
        }}
      />
    </ReactFlow>
  );
});

GraphViewInner.displayName = "GraphViewInner";

const GraphView = forwardRef((props, ref) => (
  <ReactFlowProvider>
    <GraphViewInner ref={ref} {...props} />
  </ReactFlowProvider>
));

GraphView.displayName = "GraphView";
export default GraphView;