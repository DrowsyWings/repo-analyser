from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.param_functions import Query

from backend.analyzer.graph_builder import build_graph
from backend.analyzer.parser import extract_python_imports, get_loc

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
def graph(path: str = Query(...)):
    return build_graph(path)


@app.get("/file")
def get_file(path: str):
    file_path = Path(path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        content = "Unable to read file"

    imports = []

    if file_path.suffix == ".py":
        imports = extract_python_imports(file_path)

    return {
        "name": file_path.name,
        "path": str(file_path),
        "extension": file_path.suffix,
        "loc": get_loc(file_path),
        "imports": imports,
        "content": content,
    }
