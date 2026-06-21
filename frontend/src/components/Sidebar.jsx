export default function Sidebar({ fileData }) {
  if (!fileData) {
    return <div>Select a file</div>;
  }

  return (
    <div>
      <h2>{fileData.path}</h2>

      <pre
        style={{
          textAlign: "left",
          whiteSpace: "pre-wrap",
          overflowX: "auto",
          fontFamily: "monospace",
          fontSize: "13px",
        }}
      >
        {fileData.content}
      </pre>
    </div>
  );
}
