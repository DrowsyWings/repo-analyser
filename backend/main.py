from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas.summary import SummaryResponse
from backend.services.file_service import get_file_details
from backend.services.graph_service import get_graph
from backend.services.summary_service import summarize

app = FastAPI()

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


@app.get("/graph")
def graph(path: str):
    return get_graph(path)


@app.get("/file")
def file(path: str):
    return get_file_details(path)


@app.get("/summary", response_model=SummaryResponse)
def summary(path: str):
    return summarize(path)
