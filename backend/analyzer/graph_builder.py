from pathlib import Path

from backend.analyzer.scanner import scan_repo
from backend.analyzer.parser import (
    extract_python_imports,
    get_loc,
)

def build_nodes(files):
    nodes = []

    for file in files:
        nodes.append(
            {
                "id": str(file.path),
                "label": file.name,
                "loc": get_loc(file.path),
            }
        )

    return nodes
    
def build_module_lookup(files):
    lookup = {}

    for file in files:
       path = Path(file.path)
       lookup[path.stem] = file.path

    return lookup
    
    
def build_edges(files):
    edges = []

    module_lookup = build_module_lookup(files)

    for file in files:
    
        if file.extension != ".py":
            continue
    
        imports = extract_python_imports(file.path)
        
        for imp in imports:

            root_module = imp.split(".")[0]

            if root_module not in module_lookup:
                continue

            edges.append(
                {
                    "source": file.path,
                    "target": module_lookup[root_module],
                }
            )

    return edges
    
    
def build_graph(repo_path):
    files = scan_repo(repo_path)

    return {
        "nodes": build_nodes(files),
        "edges": build_edges(files),
    }