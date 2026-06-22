from pathlib import Path


def module_name_from_path(path: Path) -> str:

    parts = list(path.with_suffix("").parts)

    try:
        idx = parts.index("backend")
        parts = parts[idx:]
    except ValueError:
        pass

    return ".".join(parts)
