import { useCallback, useEffect, useRef, useState } from "react";
import GraphView from "./components/GraphView";
import Sidebar from "./components/Sidebar";
import StatsPanel from "./components/StatsPanel";
import api from "./services/api";
import { getLayoutedElements } from "./utils/layout";
import "./index.css";

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [repoPath, setRepoPath] = useState(".");
  const [repoInput, setRepoInput] = useState(".");
  const [selectedFile, setSelectedFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [stats, setStats] = useState(null);
  const [showStats, setShowStats] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [searchDropdown, setSearchDropdown] = useState([]);
  const [graphLoading, setGraphLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sidebarWidth, setSidebarWidth] = useState(420);

  const rawNodes = useRef([]);
  const graphViewRef = useRef(null);
  const isResizing = useRef(false);

  async function loadGraph(path) {
    setGraphLoading(true);
    setError(null);
    setSelectedFile(null);
    setSummary(null);
    setSearchTerm("");
    setSearchDropdown([]);

    try {
      const [graphRes, statsRes] = await Promise.all([
        api.get("/graph", { params: { path } }),
        api.get("/stats", { params: { path } }),
      ]);

      const raw = graphRes.data;
      rawNodes.current = raw.nodes;

      const rfNodes = raw.nodes.map((node) => ({
        id: node.id,
        type: "customNode",
        position: { x: 0, y: 0 },
        style: { width: 420 },
        data: {
          label: node.label,
          path: node.path,
          loc: node.loc,
          highlighted: null,
        },
      }));

      const rfEdges = raw.edges.map((edge, i) => ({
        id: `e-${i}`,
        source: edge.source,
        target: edge.target,
        style: { stroke: "#94a3b8", strokeWidth: 1.6 },
      }));

      const layouted = getLayoutedElements(rfNodes, rfEdges);
      setNodes(layouted.nodes);
      setEdges(layouted.edges);
      setStats(statsRes.data);
    } catch (e) {
      setError("Failed to load repository. Make sure the path exists.");
    } finally {
      setGraphLoading(false);
    }
  }

  useEffect(() => { loadGraph(repoPath); }, []);

  async function handleNodeClick(_, node) {
    setSelectedFile(null);
    setSummary(null);
    setLoadingSummary(true);

    try {
      const fileRes = await api.get("/file", {
        params: { path: node.data.path, repo_path: repoPath },
      });
      setSelectedFile(fileRes.data);
    } catch (e) {
      console.error("File fetch failed:", e);
      setLoadingSummary(false);
      return;
    }

    try {
      const sumRes = await api.get("/summary", {
        params: { path: node.data.path },
      });
      setSummary(sumRes.data.summary);
    } catch (e) {
      setSummary("Failed to generate summary.");
    } finally {
      setLoadingSummary(false);
    }
  }

  function handleSearch(term) {
    setSearchTerm(term);

    if (!term.trim()) {
      setSearchDropdown([]);
      setNodes((prev) =>
        prev.map((n) => ({ ...n, data: { ...n.data, highlighted: null } }))
      );
      return;
    }

    const lower = term.toLowerCase();
    const matches = rawNodes.current.filter(
      (n) =>
        n.label.toLowerCase().includes(lower) ||
        n.path.toLowerCase().includes(lower)
    );

    setSearchDropdown(matches.slice(0, 8));

    const matchIds = new Set(matches.map((n) => n.id));
    setNodes((prev) =>
      prev.map((n) => ({
        ...n,
        data: {
          ...n.data,
          highlighted: matchIds.size === 0 ? null : matchIds.has(n.id),
        },
      }))
    );
  }
  
  function handleSearchSelect(node) {
      setSearchTerm("");
      setSearchDropdown([]);
  
      setNodes((prev) =>
          prev.map((n) => ({
              ...n,
              data: {
                  ...n.data,
                  highlighted: null,
              },
          }))
      );
  
      graphViewRef.current?.focusNode(node.id);
  
      handleNodeClick(null, {
          id: node.id,
          data: {
              path: node.path,
          },
      });
  }

  function handleRepoSubmit(e) {
    e.preventDefault();
    setRepoPath(repoInput);
    loadGraph(repoInput);
  }

  // ── Resizable sidebar ──
  const handleResizeMouseDown = useCallback((e) => {
    e.preventDefault();
    isResizing.current = true;
    document.body.style.cursor = "ew-resize";
    document.body.style.userSelect = "none";

    const startX = e.clientX;
    const startWidth = sidebarWidth;

    function onMouseMove(e) {
      if (!isResizing.current) return;
      const delta = startX - e.clientX;
      const newWidth = Math.min(Math.max(startWidth + delta, 300), 900);
      setSidebarWidth(newWidth);
    }

    function onMouseUp() {
      isResizing.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
      window.removeEventListener("mousemove", onMouseMove);
      window.removeEventListener("mouseup", onMouseUp);
    }

    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
  }, [sidebarWidth]);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-brand">
          <span className="brand-icon">⬡</span>
          <span className="brand-name">RepoAnalyser</span>
        </div>

        <form className="repo-form" onSubmit={handleRepoSubmit}>
          <input
            className="repo-input"
            value={repoInput}
            onChange={(e) => setRepoInput(e.target.value)}
            placeholder="Enter repository path…"
          />
          <button className="repo-btn" type="submit" disabled={graphLoading}>
            {graphLoading ? "Loading…" : "Analyse"}
          </button>
        </form>

        <div className="header-actions">
          <div className="search-wrapper">
            <input
              className="search-input"
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="🔍 Search files…"
            />
            {searchDropdown.length > 0 && (
              <div className="search-dropdown">
                {searchDropdown.map((n) => (
                  <button
                    key={n.id}
                    className="search-result"
                    onClick={() => handleSearchSelect(n)}
                  >
                    <span className="sr-name">{n.label}</span>
                    <span className="sr-loc">{n.loc} LOC</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <button
            className={`icon-btn ${showStats ? "active" : ""}`}
            onClick={() => setShowStats((v) => !v)}
            title="Statistics"
          >
            📊
          </button>

         
        </div>
      </header>

      <div className="app-main">
        <div className="graph-area">
          {graphLoading && (
            <div className="loading-overlay">
              <div className="spinner" />
              <p>Analysing repository…</p>
            </div>
          )}
          {error && <div className="error-banner">{error}</div>}

          <GraphView
            ref={graphViewRef}
            nodes={nodes}
            edges={edges}
            onNodeClick={handleNodeClick}
          />

          {showStats && stats && (
            <StatsPanel stats={stats} onClose={() => setShowStats(false)} />
          )}
        </div>

        <div className="sidebar-area" style={{ width: sidebarWidth }}>
          <div className="sidebar-resize-handle" onMouseDown={handleResizeMouseDown} />
          <Sidebar
            fileData={selectedFile}
            loadingSummary={loadingSummary}
            summary={summary}
          />
        </div>
      </div>
    </div>
  );
}