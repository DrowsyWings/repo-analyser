import ast
import re
from pathlib import Path


def get_loc(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return len(f.readlines())


def extract_python_imports(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read())

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return imports


_JS_PATTERNS = [
    r'import\s+(?:[\w*{}\s,]+\s+from\s+)?[\'"]([^\'"]+)[\'"]',
    r'export\s+(?:[\w*{}\s,]+\s+from\s+)?[\'"]([^\'"]+)[\'"]',
    r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
]


def extract_js_imports(filepath):
    try:
        content = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    imports = set()
    for pattern in _JS_PATTERNS:
        for match in re.finditer(pattern, content, re.MULTILINE):
            imports.add(match.group(1))

    return list(imports)


def extract_c_imports(filepath):
    try:
        content = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []

    return re.findall(r'#include\s+"([^"]+)"', content)