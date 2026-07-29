from backend.analyzer.chunker import chunk_file

PY_SOURCE = """import os
import sys

CONST = 1


def top_level():
    return 1


@staticmethod
def decorated():
    return 2


class Widget:
    def method(self):
        return 3
"""


def test_chunk_python_splits_by_symbol(tmp_path):
    f = tmp_path / "mod.py"
    f.write_text(PY_SOURCE)

    chunks = chunk_file(str(f))
    by_name = {c.name: c for c in chunks}

    assert by_name["module"].kind == "module"
    assert "import os" in by_name["module"].content

    assert by_name["top_level"].kind == "function"
    assert by_name["decorated"].kind == "function"
    assert "@staticmethod" in by_name["decorated"].content  # decorator included

    widget = by_name["Widget"]
    assert widget.kind == "class"
    assert "def method" in widget.content  # methods stay within the class chunk

    # chunks are ordered and non-overlapping
    starts = [c.start_line for c in chunks]
    assert starts == sorted(starts)


def test_chunk_non_python_uses_line_windows(tmp_path):
    f = tmp_path / "app.js"
    f.write_text("\n".join(f"line{i}" for i in range(150)))

    chunks = chunk_file(str(f))
    assert len(chunks) > 1
    assert all(c.kind == "block" for c in chunks)
    assert chunks[0].start_line == 1


def test_chunk_python_syntax_error_falls_back_to_lines(tmp_path):
    f = tmp_path / "broken.py"
    f.write_text("def oops(:\n    pass\n")

    chunks = chunk_file(str(f))
    assert chunks
    assert all(c.kind == "block" for c in chunks)


def test_chunk_empty_file(tmp_path):
    f = tmp_path / "empty.py"
    f.write_text("")
    assert chunk_file(str(f)) == []
