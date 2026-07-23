from pydantic import BaseModel


class GraphNode(BaseModel):
    id: str
    label: str
    path: str
    loc: int


class GraphEdge(BaseModel):
    source: str
    target: str


class GraphResponse(BaseModel):
    node_count: int
    edge_count: int
    nodes: list[GraphNode]
    edges: list[GraphEdge]
