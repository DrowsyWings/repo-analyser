const EXT_NAMES = {
  ".py":  "Python",
  ".js":  "JavaScript",
  ".ts":  "TypeScript",
  ".jsx": "React JSX",
  ".tsx": "React TSX",
  ".cpp": "C++",
  ".c":   "C",
  ".h":   "C Header",
  ".hpp": "C++ Header",
};

const EXT_COLORS = {
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

export default function StatsPanel({ stats, onClose }) {
  const langs = stats.languages || {};
  const maxCount = Math.max(...Object.values(langs), 1);

  return (
    <div className="stats-panel">
      <div className="stats-header">
        <span className="stats-title">Repository Stats</span>
        <button className="close-btn" onClick={onClose}>✕</button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{stats.total_files}</div>
          <div className="stat-label">Total Files</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.total_loc.toLocaleString()}</div>
          <div className="stat-label">Total LOC</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.average_loc}</div>
          <div className="stat-label">Avg LOC</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{Object.keys(langs).length}</div>
          <div className="stat-label">Languages</div>
        </div>
      </div>

      <div className="stats-section">
        <div className="stats-section-title">Language Breakdown</div>
        {Object.entries(langs).map(([ext, count]) => (
          <div key={ext} className="lang-row">
            <span className="lang-name" style={{ color: EXT_COLORS[ext] || "#888" }}>
              {EXT_NAMES[ext] || ext}
            </span>
            <div className="lang-bar-wrap">
              <div
                className="lang-bar"
                style={{
                  width: `${(count / maxCount) * 100}%`,
                  background: EXT_COLORS[ext] || "#555",
                }}
              />
            </div>
            <span className="lang-count">{count}</span>
          </div>
        ))}
      </div>

      <div className="stats-section">
        <div className="stats-section-title">Largest Files</div>
        {stats.largest_files.map((f, i) => (
          <div key={f.path} className="largest-row">
            <span className="lf-rank">#{i + 1}</span>
            <span className="lf-name">{f.name}</span>
            <span className="lf-loc">{f.loc} LOC</span>
          </div>
        ))}
      </div>
    </div>
  );
}