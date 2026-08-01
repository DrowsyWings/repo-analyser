from pydantic import BaseModel


class ChatRequest(BaseModel):
    repo_path: str
    question: str


class Citation(BaseModel):
    path: str
    name: str
    start_line: int
    end_line: int


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
