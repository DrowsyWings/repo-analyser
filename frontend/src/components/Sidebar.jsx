export default function Sidebar({ selectedNode }) {
  if (!selectedNode) {
    return <div>Select a file</div>;
  }

  return (
    <div>
      <h2>{selectedNode.data.label}</h2>
      <p>{selectedNode.id}</p>
    </div>
  );
}
