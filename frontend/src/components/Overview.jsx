import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import api from "../services/api";

export default function Overview({ repoPath, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    api
      .get("/overview", { params: { path: repoPath } })
      .then((res) => {
        if (active) {
          setData(res.data);
          setLoading(false);
        }
      })
      .catch(() => {
        if (active) {
          setError("Failed to generate overview.");
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [repoPath]);

  return (
    <div className="overview-panel">
      <div className="chat-header">
        <span className="chat-title">📄 Architecture Overview</span>
        <button className="close-btn" onClick={onClose}>
          ✕
        </button>
      </div>

      <div className="overview-body">
        {loading && (
          <div className="overview-loading">
            <div className="spinner" />
            <p>Generating overview…</p>
          </div>
        )}
        {error && <p className="stats-empty">{error}</p>}
        {data && (
          <div className="chat-markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {data.overview}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}
