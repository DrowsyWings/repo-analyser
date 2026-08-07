from evals.harness import evaluate, to_markdown

DATASET = [
    {"question": "where is X", "expected_files": ["a.py"]},
    {"question": "where is Y", "expected_files": ["z.py"]},
]


def _fake_retrieve(question, k):
    if "X" in question:
        return [{"metadata": {"path": "/repo/a.py"}}]
    return [{"metadata": {"path": "/repo/b.py"}}]  # miss for Y


def test_evaluate_computes_hit_rate():
    report = evaluate(DATASET, _fake_retrieve)
    assert report["hit_rate"] == 0.5
    assert report["rows"][0]["hit"] is True
    assert report["rows"][1]["hit"] is False
    assert report["rows"][0]["top"] == "a.py"


def test_to_markdown_has_table_and_rate():
    md = to_markdown(evaluate(DATASET, _fake_retrieve))
    assert "| Question |" in md
    assert "hit@5" in md
