from fastapi import FastAPI
from fastapi.param_functions import Query

from backend.analyzer.graph_builder import build_graph
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware( CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "working"}


@app.get("/graph")
def graph(path: str = Query(...)):
    return build_graph(path)