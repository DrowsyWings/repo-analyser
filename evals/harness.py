from pathlib import Path


def evaluate(dataset: list[dict], retrieve_fn, k: int = 5) -> dict:
    """Score retrieval: a question is a hit if any expected file is retrieved."""
    rows = []
    hits = 0
    for item in dataset:
        paths = [h["metadata"]["path"] for h in retrieve_fn(item["question"], k)]
        hit = any(exp in path for exp in item["expected_files"] for path in paths)
        hits += int(hit)
        rows.append(
            {
                "question": item["question"],
                "expected": item["expected_files"],
                "top": Path(paths[0]).name if paths else "-",
                "hit": hit,
            }
        )

    hit_rate = hits / len(dataset) if dataset else 0.0
    return {"hit_rate": hit_rate, "rows": rows, "k": k}


def to_markdown(report: dict) -> str:
    lines = [
        "| Question | Expected | Top retrieved | Hit |",
        "|---|---|---|---|",
    ]
    for row in report["rows"]:
        mark = "✅" if row["hit"] else "❌"
        lines.append(
            f"| {row['question']} | {', '.join(row['expected'])} | {row['top']} | {mark} |"
        )
    lines.append("")
    lines.append(
        f"**Retrieval hit@{report['k']}: {report['hit_rate'] * 100:.0f}%** "
        f"({len(report['rows'])} questions)"
    )
    return "\n".join(lines)
