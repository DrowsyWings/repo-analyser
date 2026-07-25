from pydantic import BaseModel

from backend.schemas.graph import GraphResponse


class AnalyzeRequest(BaseModel):
    repo_url: str


class AnalyzeResponse(BaseModel):
    path: str
    graph: GraphResponse
