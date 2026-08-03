import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import api from "../services/api";

function fileName(path) {
  return path.split(/[\\/]/).pop();
}

export default function Chat({ repoPath, onCitationClick, onClose }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const sourceRef = useRef(null);

  function patchLast(update) {
    setMessages((prev) => {
      const copy = [...prev];
      copy[copy.length - 1] = { ...copy[copy.length - 1], ...update };
      return copy;
    });
  }

  function ask(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || streaming) return;

    setInput("");
    setMessages((prev) => [
      ...prev,
      { role: "user", text: question },
      { role: "assistant", text: "", citations: [] },
    ]);
    setStreaming(true);

    const url = `${api.defaults.baseURL}/chat/stream?repo_path=${encodeURIComponent(
      repoPath,
    )}&question=${encodeURIComponent(question)}`;
    const source = new EventSource(url);
    sourceRef.current = source;

    source.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "token") {
        setMessages((prev) => {
          const copy = [...prev];
          const last = copy[copy.length - 1];
          copy[copy.length - 1] = { ...last, text: last.text + data.text };
          return copy;
        });
      } else if (data.type === "done") {
        source.close();
        setStreaming(false);
        patchLast({ citations: data.citations || [] });
      } else if (data.type === "error") {
        source.close();
        setStreaming(false);
        patchLast({ text: `Error: ${data.detail || "request failed"}` });
      }
    };

    source.onerror = () => {
      source.close();
      setStreaming(false);
    };
  }

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <span className="chat-title">💬 Chat with this repo</span>
        <button className="close-btn" onClick={onClose}>
          ✕
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <p className="chat-hint">
            Ask about this codebase — e.g. “Where is authentication handled?”
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`chat-msg ${msg.role}`}>
            {msg.role === "assistant" ? (
              <div className="chat-markdown">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.text || "…"}
                </ReactMarkdown>
                {msg.citations?.length > 0 && (
                  <div className="chat-citations">
                    {msg.citations.map((c) => (
                      <button
                        key={`${c.path}:${c.start_line}`}
                        className="citation-chip"
                        title={`${c.path} (lines ${c.start_line}-${c.end_line})`}
                        onClick={() => onCitationClick(c.path)}
                      >
                        {fileName(c.path)}
                        <span className="cite-lines">:{c.start_line}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <span>{msg.text}</span>
            )}
          </div>
        ))}
      </div>

      <form className="chat-input-row" onSubmit={ask}>
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about this codebase…"
          disabled={streaming}
        />
        <button
          className="chat-send"
          type="submit"
          disabled={streaming || !input.trim()}
        >
          {streaming ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}
