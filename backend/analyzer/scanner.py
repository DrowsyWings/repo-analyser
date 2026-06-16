from dataclasses import dataclass
from pathlib import Path

SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".cpp", ".c", ".h", ".hpp"}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "__pycache__",
    ".venv",
}


@dataclass
class FileInfo:
    path: str
    name: str
    extension: str
    module_name: str

 
def get_module_name(path: Path) -> str:
    
    parts = list(path.with_suffix("").parts)
    
    try:
        idx = parts.index("backend")
        parts = parts[idx:]
    except ValueError:
        pass
    
    return ".".join(parts)
 

def scan_repo(root: str) -> list[FileInfo]:
    files = []

    for path in Path(root).rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue

        if path.is_file() and path.suffix in SUPPORTED_EXTENSIONS:
            files.append(
                FileInfo(
                    path=str(path.resolve()),
                    name=path.name,
                    extension=path.suffix,
                    module_name=get_module_name(path)
                )
            )

    return files
   