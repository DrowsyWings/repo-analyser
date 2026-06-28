import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";

const EXT_LANG = {
  ".py":  "python",
  ".js":  "javascript",
  ".jsx": "jsx",
  ".ts":  "typescript",
  ".tsx": "tsx",
  ".cpp": "cpp",
  ".c":   "c",
  ".h":   "c",
  ".hpp": "cpp",
};

function Card({ title, children }) {
  return (
    <div className="sidebar-card">
      <div className="card-title">{title}</div>
      <div className="card-body">{children}</div>
    </div>
  );
}

function TagList({ items, emptyMsg }) {
  if (!items || items.length === 0)
    return <span className="empty-label">{emptyMsg}</span>;
  return (
    <div className="tag-list">
      {items.map((item) => (
        <span key={item} className="tag">{item}</span>
      ))}
    </div>
  );
}

export default function Sidebar({ fileData, loadingSummary, summary }) {
  if (!fileData) {
    return (
      <div className="sidebar-empty">
        <div className="empty-icon">⬡</div>
        <div className="empty-title">Repository Inspector</div>
        <div className="empty-desc">Click any node to inspect a file</div>
      </div>
    );
  }

  const lang = EXT_LANG[fileData.extension] || "text";

  return (
    <div className="sidebar-content">
      <div className="sidebar-heading">
        <span className="file-icon">📄</span>
        <span className="file-name">{fileData.name}</span>
      </div>

      <Card title="Overview">
        <div className="overview-grid">
          <span className="ov-key">Path</span>
          <span className="ov-val">{fileData.path}</span>
          <span className="ov-key">Extension</span>
          <span className="ov-val">{fileData.extension}</span>
          <span className="ov-key">Lines of Code</span>
          <span className="ov-val loc-val">{fileData.loc}</span>
        </div>
      </Card>

      <Card title="Dependencies">
        <div className="dep-section">
          <div className="dep-label">Imports</div>
          <TagList items={fileData.imports} emptyMsg="No imports" />
        </div>
        <div className="dep-section">
          <div className="dep-label">Imported By</div>
          <TagList items={fileData.imported_by} emptyMsg="Not imported by anything" />
        </div>
      </Card>

      <Card title="🤖 AI Summary">
        {loadingSummary ? (
          <div className="ai-loading">
            <div className="spinner-sm" />
            <span>Generating summary…</span>
          </div>
        ) : summary ? (
          <div className="markdown-body">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {summary}
            </ReactMarkdown>
          </div>
        ) : (
          <span className="empty-label">No summary available</span>
        )}
      </Card>

      <Card title="Source Code">
        <SyntaxHighlighter
          language={lang}
          style={vscDarkPlus}
          showLineNumbers
          wrapLongLines={false}
          customStyle={{
            margin: 0,
            borderRadius: "6px",
            fontSize: "11px",
            maxHeight: "420px",
          }}
        >
          {fileData.content}
        </SyntaxHighlighter>
      </Card>
    </div>
  );
}