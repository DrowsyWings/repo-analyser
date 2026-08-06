import os
from collections import defaultdict
from pathlib import Path

from google import genai

from backend.config import MODEL
from backend.services.graph_service import get_graph

MAX_FILES_PER_MODULE = 15
HEAD_LINES = 40

_client = None
_overview_cache: dict = {}


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


MODULE_PROMPT = """Summarize this module of a codebase in 2-3 sentences:
its purpose and main responsibilities.

Module: {name}
Files and snippets:
{context}
"""

REDUCE_PROMPT = """You are onboarding a new developer to a codebase.
Using the module summaries below, write a concise one-page overview in markdown:
- What this project is and does
- How it is structured (the main modules and how they relate)
- A suggested reading order (which files/modules to read first)

Module summaries:
{summaries}
"""


def _file_head(path: str) -> str:
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""
    return "\n".join(lines[:HEAD_LINES])


def _module_context(nodes: list[dict]) -> str:
    return "\n\n".join(
        f"## {node['label']}\n{_file_head(node['path'])}"
        for node in nodes[:MAX_FILES_PER_MODULE]
    )


def _generate(prompt: str) -> str:
    return _get_client().models.generate_content(model=MODEL, contents=prompt).text


def generate_overview(repo_path: str) -> dict:
    if repo_path in _overview_cache:
        return _overview_cache[repo_path]

    nodes = get_graph(repo_path)["nodes"]
    if not nodes:
        result = {
            "overview": "No analysable source files were found in this repository.",
            "modules": [],
        }
        _overview_cache[repo_path] = result
        return result

    modules: dict[str, list] = defaultdict(list)
    for node in nodes:
        modules[node.get("community") or "misc"].append(node)

    module_summaries = []
    for name, mod_nodes in sorted(modules.items()):
        summary = _generate(
            MODULE_PROMPT.format(name=name, context=_module_context(mod_nodes))
        )
        module_summaries.append({"module": name, "summary": summary})

    joined = "\n\n".join(f"### {m['module']}\n{m['summary']}" for m in module_summaries)
    overview = _generate(REDUCE_PROMPT.format(summaries=joined))

    result = {"overview": overview, "modules": module_summaries}
    _overview_cache[repo_path] = result
    return result


def clear_overview_cache() -> None:
    _overview_cache.clear()
