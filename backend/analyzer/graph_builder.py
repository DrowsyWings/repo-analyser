from pathlib import Path

from backend.analyzer.parser import (
    extract_c_imports,
    extract_js_imports,
    extract_python_imports,
    get_loc,
)
from backend.analyzer.scanner import scan_repo

JS_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx"}
C_EXTENSIONS  = {".c", ".cpp", ".h", ".hpp"}


def build_nodes(files):
    nodes = []
    for file in files:
        nodes.append({
            "id":    str(file.module_name),
            "label": file.name,
            "path":  file.path,
            "loc":   get_loc(file.path),
        })
    return nodes


def build_module_lookup(files):
    return {file.module_name: file for file in files}


def build_path_lookup(files):
    return {file.path: file for file in files}


def resolve_js_import(from_path: str, import_path: str, path_lookup: dict):
    base_dir = Path(from_path).parent
    resolved = (base_dir / import_path).resolve()

    if str(resolved) in path_lookup:
        return path_lookup[str(resolved)]

    for ext in [".js", ".jsx", ".ts", ".tsx"]:
        candidate = str(resolved.with_suffix(ext))
        if candidate in path_lookup:
            return path_lookup[candidate]

    for ext in [".js", ".jsx", ".ts", ".tsx"]:
        candidate = str(resolved / f"index{ext}")
        if candidate in path_lookup:
            return path_lookup[candidate]

    return None


def resolve_c_import(from_path: str, include_path: str, path_lookup: dict):
    base_dir = Path(from_path).parent
    resolved = str((base_dir / include_path).resolve())
    return path_lookup.get(resolved)


def build_edges(files):
    edges = []
    module_lookup = build_module_lookup(files)
    path_lookup   = build_path_lookup(files)

    for file in files:
        if file.extension == ".py":
            imports = extract_python_imports(file.path)
            for imp in imports:
                if imp not in module_lookup:
                    continue
                edges.append({
                    "source": file.module_name,
                    "target": module_lookup[imp].module_name,
                })

        elif file.extension in JS_EXTENSIONS:
            imports = extract_js_imports(file.path)
            for imp in imports:
                if not imp.startswith("."):
                    continue  # skip external packages like react, axios
                target = resolve_js_import(file.path, imp, path_lookup)
                if target:
                    edges.append({
                        "source": file.module_name,
                        "target": target.module_name,
                    })

        elif file.extension in C_EXTENSIONS:
            imports = extract_c_imports(file.path)
            for imp in imports:
                target = resolve_c_import(file.path, imp, path_lookup)
                if target:
                    edges.append({
                        "source": file.module_name,
                        "target": target.module_name,
                    })

    return edges


def build_graph(repo_path):
    files = scan_repo(repo_path)
    nodes = build_nodes(files)
    edges = build_edges(files)

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes":      nodes,
        "edges":      edges,
    }


def build_reverse_lookup(edges):
    reverse = {}
    for edge in edges:
        target = edge["target"]
        source = edge["source"]
        if target not in reverse:
            reverse[target] = []
        reverse[target].append(source)
    return reverse