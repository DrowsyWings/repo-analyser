from fastapi import FastAPI
from fastapi.param_functions import Query

from backend.analyzer.graph_builder import build_graph

app = FastAPI()


@app.get("/")
def root():
    return {"status": "working"}


@app.get("/graph")
def graph(path: str = Query(...)):
    return build_graph(path)