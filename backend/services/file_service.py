from pathlib import Path

from backend.analyzer.graph_builder import build_reverse_lookup
from backend.analyzer.parser import extract_python_imports, get_loc
from backend.services.graph_service import get_graph
from backend.utils.path_utils import module_name_from_path


def get_file_details(path: str, repo_path: str = "."):
    file_path = Path(path)

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        content = "Unable to read file."

    imports: list = []

    if file_path.suffix == ".py":
        try:
            imports = extract_python_imports(file_path)
        except Exception:
            imports = []

    graph = get_graph(repo_path)
    reverse = build_reverse_lookup(graph["edges"])
    module_name = module_name_from_path(file_path)
    imported_by = reverse.get(module_name, [])

    return {
        "name": file_path.name,
        "path": str(file_path),
        "extension": file_path.suffix,
        "loc": get_loc(file_path),
        "imports": imports,
        "imported_by": imported_by,
        "content": content,
    }
