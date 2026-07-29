import ast
from dataclasses import dataclass
from pathlib import Path

LINE_WINDOW = 60
LINE_OVERLAP = 10


@dataclass
class Chunk:
    path: str
    name: str
    kind: str  # "function" | "class" | "module" | "block"
    start_line: int
    end_line: int
    content: str


def chunk_file(path: str) -> list[Chunk]:
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    if p.suffix == ".py":
        try:
            return _chunk_python(str(p), text)
        except SyntaxError:
            pass  # malformed source — fall back to line windows

    return _chunk_by_lines(str(p), text)


def _slice(lines: list[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1 : end])


def _symbol_span(node) -> tuple[int, int]:
    start = node.lineno
    for decorator in getattr(node, "decorator_list", []):
        start = min(start, decorator.lineno)
    return start, node.end_lineno


def _chunk_python(path: str, text: str) -> list[Chunk]:
    tree = ast.parse(text)
    lines = text.splitlines()
    chunks: list[Chunk] = []
    buffer: list[tuple[int, int]] = []

    def flush_module():
        if buffer:
            start = buffer[0][0]
            end = buffer[-1][1]
            chunks.append(
                Chunk(path, "module", "module", start, end, _slice(lines, start, end))
            )
            buffer.clear()

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            flush_module()
            start, end = _symbol_span(node)
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            chunks.append(
                Chunk(path, node.name, kind, start, end, _slice(lines, start, end))
            )
        else:
            end = node.end_lineno or node.lineno
            buffer.append((node.lineno, end))

    flush_module()
    return chunks


def _chunk_by_lines(path: str, text: str) -> list[Chunk]:
    lines = text.splitlines()
    if not lines:
        return []

    step = LINE_WINDOW - LINE_OVERLAP
    chunks: list[Chunk] = []
    i = 0
    n = len(lines)
    while i < n:
        start = i + 1
        end = min(i + LINE_WINDOW, n)
        chunks.append(
            Chunk(
                path,
                f"lines {start}-{end}",
                "block",
                start,
                end,
                "\n".join(lines[i:end]),
            )
        )
        if end >= n:
            break
        i += step

    return chunks
