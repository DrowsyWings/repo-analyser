import { memo } from "react";
import { Handle, Position } from "reactflow";

const LANG_CONFIG = {
  ".py": { label: "PY", color: "#3776ab", bg: "#1a3456" },
  ".js": { label: "JS", color: "#c8a428", bg: "#2d2400" },
  ".ts": { label: "TS", color: "#3178c6", bg: "#142040" },
  ".jsx": { label: "JSX", color: "#61dafb", bg: "#003040" },
  ".tsx": { label: "TSX", color: "#61dafb", bg: "#003040" },
  ".cpp": { label: "C++", color: "#9560b0", bg: "#20103a" },
  ".c": { label: "C", color: "#7cacbf", bg: "#0f2030" },
  ".h": { label: "H", color: "#7cacbf", bg: "#0f2030" },
  ".hpp": { label: "HPP", color: "#9560b0", bg: "#20103a" },
};

const DEFAULT = { label: "FILE", color: "#666", bg: "#2a2a2a" };

const CustomNode = memo(({ data, selected }) => {
  const ext = data.path ? "." + data.path.split(".").pop() : "";
  const lang = LANG_CONFIG[ext] || DEFAULT;

  // const isHighlighted = data.highlighted === true;
  const state = data.state ?? "normal";

  const isSelected = state === "selected";
  const isNeighbor = state === "neighbor";
  const isDimmed = state === "dim";

  // const isDimmed = data.highlighted === false;

  return (
    <div
      className="custom-node"
      style={{
        width: "100%",
        borderLeftColor: isSelected
          ? "var(--accent)"
          : isNeighbor
            ? lang.color
            : "#94a3b8",
        borderColor: selected ? "var(--accent)" : undefined,
        opacity: isDimmed ? 0.55 : 1,
        boxShadow: isSelected
          ? "0 0 0 2px var(--accent)"
          : isNeighbor
            ? `0 0 12px ${lang.color}55`
            : "none",
        transition: "opacity 0.2s, box-shadow 0.2s, transform 0.15s",
      }}
    >
      <Handle type="target" position={Position.Top} className="node-handle" />

      <div className="node-header">
        <span className="node-filename" title={data.path}>
          {data.label}
        </span>
        <span
          className="node-lang-badge"
          style={{
            background: lang.bg,
            color: lang.color,
            border: `1px solid ${lang.color}50`,
          }}
        >
          {lang.label}
        </span>
      </div>

      <div className="node-footer">
        <span className="node-loc">{data.loc} LOC</span>
      </div>

      <Handle
        type="source"
        position={Position.Bottom}
        className="node-handle"
      />
    </div>
  );
});

CustomNode.displayName = "CustomNode";
export default CustomNode;
