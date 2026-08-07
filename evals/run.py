import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv  # noqa: E402

from backend.services.rag_service import ensure_index, retrieve  # noqa: E402
from evals.harness import evaluate, to_markdown  # noqa: E402


def main() -> None:
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    load_dotenv("backend/.env")

    dataset = json.loads((Path(__file__).parent / "dataset.json").read_text())
    ensure_index(repo_path)

    report = evaluate(dataset, lambda q, k: retrieve(repo_path, q, k=k))
    print(to_markdown(report))


if __name__ == "__main__":
    main()
