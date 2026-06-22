export default function Sidebar({ fileData }) {
  if (!fileData) {
    return (
      <div style={{ padding: "20px" }}>
        <h2>Repository Inspector</h2>
        <p>Select a node.</p>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: "20px",
        overflowY: "auto",
        height: "100%",
        textAlign: "left",
      }}
    >
      <h2>{fileData.name}</h2>

      <hr />

      <h3>📁 Path</h3>

      <p style={{ wordBreak: "break-word" }}>{fileData.path}</p>

      <h3>📄 Extension</h3>

      <p>{fileData.extension}</p>

      <h3>📏 Lines of Code</h3>

      <p>{fileData.loc}</p>

      <h3>📦 Imports</h3>

      {fileData.imports.length === 0 ? (
        <p>No imports</p>
      ) : (
        <ul>
          {fileData.imports.map((imp) => (
            <li key={imp}>{imp}</li>
          ))}
        </ul>
      )}

      <hr />

      <h3>Code</h3>

      <pre
        style={{
          background: "#1e1e1e",
          color: "#ddd",
          padding: "12px",
          borderRadius: "8px",
          overflowX: "auto",
          whiteSpace: "pre-wrap",
          fontSize: "13px",
          fontFamily: "monospace",
        }}
      >
        {fileData.content}
      </pre>
    </div>
  );
}
