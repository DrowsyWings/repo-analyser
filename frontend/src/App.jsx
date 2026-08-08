import { useCallback, useRef, useState } from "react";
import Chat from "./components/Chat";
import GraphView from "./components/GraphView";
import Overview from "./components/Overview";
import Sidebar from "./components/Sidebar";
import StatsPanel from "./components/StatsPanel";
import api from "./services/api";
import { getLayoutedElements } from "./utils/layout";
import { highlightGraph } from "./utils/graphUtils";
import "./index.css";

const STAGE_PCT = {
  starting: 8,
  resolving: 30,
  downloading: 65,
  building: 88,
};

const EXAMPLE_REPOS = [
  { label: "pallets/flask", url: "https://github.com/pallets/flask" },
  { label: "psf/requests", url: "https://github.com/psf/requests" },
  { label: "expressjs/express", url: "https://github.com/expressjs/express" },
];

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [repoPath, setRepoPath] = useState(".");
  const [repoInput, setRepoInput] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [stats, setStats] = useState(null);
  const [showStats, setShowStats] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [showOverview, setShowOverview] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [searchDropdown, setSearchDropdown] = useState([]);
  const [modules, setModules] = useState([]);
  const [enabledModules, setEnabledModules] = useState(new Set());
  const [graphLoading, setGraphLoading] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);
  const [sidebarWidth, setSidebarWidth] = useState(420);

  const rawNodes = useRef([]);
  const rawEdges = useRef([]);

  const graphViewRef = useRef(null);
  const isResizing = useRef(false);
  const rawNodesRendered = useRef([]);

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

      const moduleNames = [
        ...new Set(raw.nodes.map((n) => n.community).filter(Boolean)),
      ].sort();

      setModules(moduleNames);
      setEnabledModules(new Set(moduleNames));

      const rfNodes = raw.nodes.map((node) => ({
        id: node.id,
        type: "customNode",
        position: { x: 0, y: 0 },
        style: { width: 420 },
        data: {
          label: node.label,
          path: node.path,
          loc: node.loc,
          community: node.community,
          highlighted: null,
        },
      }));

      const rfEdges = raw.edges.map((edge, i) => ({
        id: `e-${i}`,
        source: edge.source,
        target: edge.target,
        style: { stroke: "#94a3b8", strokeWidth: 1.6 },
      }));

      rawEdges.current = rfEdges;

      const layouted = getLayoutedElements(rfNodes, rfEdges);
      rawNodesRendered.current = layouted.nodes;
      setNodes(layouted.nodes);
      setEdges(layouted.edges);
      setTimeout(() => {
        clearGraphHighlight();
      }, 0);
      setStats(statsRes.data);
    } catch (e) {
      console.error(e);
      console.error(e.response);
      console.error(e.response?.data);
      setError("Failed to load repository. Make sure the path exists.");
    } finally {
      setGraphLoading(false);
    }
  }

  function clearGraphHighlight() {
    setNodes(rawNodesRendered.current);
    setEdges(rawEdges.current);
  }
  function toggleModule(module) {
    const next = new Set(enabledModules);

    if (next.has(module)) next.delete(module);
    else next.add(module);

    setEnabledModules(next);

    const filteredNodes = rawNodesRendered.current.filter((n) =>
      next.has(n.data.community),
    );

    const ids = new Set(filteredNodes.map((n) => n.id));

    const filteredEdges = rawEdges.current.filter(
      (e) => ids.has(e.source) && ids.has(e.target),
    );

    setNodes(filteredNodes);
    setEdges(filteredEdges);
  }

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
    } catch {
      setSummary("Failed to generate summary.");
    } finally {
      setLoadingSummary(false);
    }
  }

  function handleGraphClick(_, node) {
    const highlighted = highlightGraph(
      rawNodesRendered.current,
      rawEdges.current,
      node.id,
    );

    setNodes(highlighted.nodes);
    setEdges(highlighted.edges);

    handleNodeClick(_, node);
  }

  function handleSearch(term) {
    setSearchTerm(term);

    if (!term.trim()) {
      setSearchDropdown([]);
      setNodes((prev) =>
        prev.map((n) => ({ ...n, data: { ...n.data, highlighted: null } })),
      );
      return;
    }

    const lower = term.toLowerCase();
    const matches = rawNodes.current.filter(
      (n) =>
        n.label.toLowerCase().includes(lower) ||
        n.path.toLowerCase().includes(lower),
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
      })),
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
      })),
    );

    graphViewRef.current?.focusNode(node.id);

    const highlighted = highlightGraph(
      rawNodesRendered.current,
      rawEdges.current,
      node.id,
    );

    setNodes(highlighted.nodes);
    setEdges(highlighted.edges);

    handleNodeClick(null, {
      id: node.id,
      data: {
        path: node.path,
      },
    });
  }

  function focusByPath(path) {
    const node = rawNodes.current.find((n) => n.path === path);
    if (!node) return;

    graphViewRef.current?.focusNode(node.id);

    const highlighted = highlightGraph(
      rawNodesRendered.current,
      rawEdges.current,
      node.id,
    );
    setNodes(highlighted.nodes);
    setEdges(highlighted.edges);

    handleNodeClick(null, { id: node.id, data: { path: node.path } });
  }

  function analyzeRepo(url) {
    const trimmed = url.trim();
    if (!trimmed) return;

    setGraphLoading(true);
    setError(null);
    setProgress({ stage: "starting", message: "Starting analysis…" });

    const streamUrl = `${api.defaults.baseURL}/analyze/stream?repo_url=${encodeURIComponent(
      trimmed,
    )}`;
    const source = new EventSource(streamUrl);

    source.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.stage === "error") {
        source.close();
        setGraphLoading(false);
        setProgress(null);
        setError(data.detail || "Failed to analyse repository.");
        return;
      }

      if (data.stage === "done") {
        source.close();
        setProgress(null);
        setRepoPath(data.path);
        loadGraph(data.path);
        return;
      }

      setProgress({ stage: data.stage, message: data.message });
    };

    source.onerror = () => {
      source.close();
      setGraphLoading(false);
      setProgress(null);
      setError("Lost connection to the server.");
    };
  }

  function handleRepoSubmit(e) {
    e.preventDefault();
    analyzeRepo(repoInput);
  }

  // ── Resizable sidebar ──
  const handleResizeMouseDown = useCallback(
    (e) => {
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
    },
    [sidebarWidth],
  );

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
            type="url"
            value={repoInput}
            onChange={(e) => setRepoInput(e.target.value)}
            placeholder="https://github.com/owner/repo"
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
          <div className="module-filter">
            {modules.map((m) => (
              <button
                key={m}
                className={`module-chip ${
                  enabledModules.has(m) ? "active" : ""
                }`}
                onClick={() => toggleModule(m)}
              >
                {m}
              </button>
            ))}
          </div>

          <button
            className={`icon-btn ${showOverview ? "active" : ""}`}
            onClick={() => setShowOverview((v) => !v)}
            title="Architecture overview"
            disabled={nodes.length === 0}
          >
            📄
          </button>
          <button
            className={`icon-btn ${showChat ? "active" : ""}`}
            onClick={() => setShowChat((v) => !v)}
            title="Chat with repo"
            disabled={nodes.length === 0}
          >
            💬
          </button>
          <button
            className={`icon-btn ${showStats ? "active" : ""}`}
            onClick={() => setShowStats((v) => !v)}
            title="Statistics"
          >
            📊
          </button>
          <button
            className="icon-btn"
            onClick={() => graphViewRef.current?.exportPNG()}
            title="Export graph as PNG"
            disabled={nodes.length === 0}
          >
            🖼️
          </button>
          <button
            className="icon-btn"
            onClick={clearGraphHighlight}
            title="Clear Selection"
          >
            ✕
          </button>
        </div>
      </header>

      <div className="app-main">
        <div className="graph-area">
          {graphLoading && (
            <div className="loading-overlay">
              <div className="spinner" />
              <p>{progress?.message || "Analysing repository…"}</p>
              {progress && (
                <div className="progress-track">
                  <div
                    className="progress-fill"
                    style={{ width: `${STAGE_PCT[progress.stage] ?? 10}%` }}
                  />
                </div>
              )}
            </div>
          )}
          {error && <div className="error-banner">{error}</div>}

          {!graphLoading && nodes.length === 0 && (
            <div className="empty-state">
              <span className="empty-icon">⬡</span>
              <h2>Analyse any public GitHub repository</h2>
              <p>Paste a repository URL above, or try one of these:</p>
              <div className="example-repos">
                {EXAMPLE_REPOS.map((ex) => (
                  <button
                    key={ex.url}
                    className="example-chip"
                    onClick={() => {
                      setRepoInput(ex.url);
                      analyzeRepo(ex.url);
                    }}
                  >
                    {ex.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          <GraphView
            ref={graphViewRef}
            nodes={nodes}
            edges={edges}
            onNodeClick={handleGraphClick}
            onPaneClick={clearGraphHighlight}
          />

          {showStats && stats && (
            <StatsPanel
              stats={stats}
              onClose={() => setShowStats(false)}
              onFileClick={focusByPath}
            />
          )}

          {showChat && nodes.length > 0 && (
            <Chat
              repoPath={repoPath}
              onCitationClick={focusByPath}
              onClose={() => setShowChat(false)}
            />
          )}

          {showOverview && nodes.length > 0 && (
            <Overview
              repoPath={repoPath}
              onClose={() => setShowOverview(false)}
            />
          )}
        </div>

        <div className="sidebar-area" style={{ width: sidebarWidth }}>
          <div
            className="sidebar-resize-handle"
            onMouseDown={handleResizeMouseDown}
          />
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
