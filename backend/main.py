import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from backend.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.schemas.file import FileResponse
from backend.schemas.graph import GraphResponse
from backend.schemas.overview import OverviewResponse
from backend.schemas.summary import SummaryResponse
from backend.services.file_service import get_file_details
from backend.services.graph_service import get_graph, get_stats
from backend.services.ingest_service import (
    RepoDownloadError,
    download_github_repo,
    iter_download_steps,
)
from backend.services.overview_service import generate_overview
from backend.services.rag_service import answer_question, stream_answer
from backend.services.summary_service import summarize

app = FastAPI(title="RepoAnalyser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "working"}


@app.get("/graph", response_model=GraphResponse)
def graph(path: str = "."):
    return get_graph(path)


@app.get("/stats")
def stats(path: str = "."):
    return get_stats(path)


@app.get("/file", response_model=FileResponse)
def file(path: str, repo_path: str = "."):
    return get_file_details(path, repo_path)


@app.get("/summary", response_model=SummaryResponse)
def summary(path: str):
    return summarize(path)


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    try:
        path = download_github_repo(req.repo_url)
    except RepoDownloadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"path": str(path), "graph": get_graph(str(path))}


def _sse(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


@app.get("/overview", response_model=OverviewResponse)
def overview(path: str = "."):
    return generate_overview(path)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    return answer_question(req.repo_path, req.question)


@app.get("/chat/stream")
def chat_stream(repo_path: str, question: str):
    def events():
        try:
            for event in stream_answer(repo_path, question):
                yield _sse(event)
        except Exception as exc:
            yield _sse({"type": "error", "detail": str(exc)})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/analyze/stream")
def analyze_stream(repo_url: str):
    def events():
        steps = iter_download_steps(repo_url)
        try:
            while True:
                try:
                    stage, message = next(steps)
                except StopIteration as stop:
                    path = stop.value
                    break
                yield _sse({"stage": stage, "message": message})

            yield _sse({"stage": "building", "message": "Building dependency graph"})
            graph = get_graph(str(path))
            yield _sse({"stage": "done", "path": str(path), "graph": graph})
        except RepoDownloadError as exc:
            yield _sse({"stage": "error", "detail": str(exc)})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
