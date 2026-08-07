from backend.services import graph_service, overview_service


class _FakeModels:
    def __init__(self):
        self.calls = 0

    def generate_content(self, model, contents):
        self.calls += 1
        text = f"response-{self.calls}"
        return type("R", (), {"text": text})()


class _FakeClient:
    def __init__(self):
        self.models = _FakeModels()


def _tiny_repo(tmp_path):
    (tmp_path / "a.py").write_text("import b\n\n\ndef alpha():\n    return 1\n")
    (tmp_path / "b.py").write_text("def beta():\n    return 2\n")
    return str(tmp_path)


def test_generate_overview_maps_modules_then_reduces(tmp_path, monkeypatch):
    repo = _tiny_repo(tmp_path)
    graph_service.clear_graph_cache()
    overview_service.clear_overview_cache()

    fake = _FakeClient()
    monkeypatch.setattr(overview_service, "_get_client", lambda: fake)

    result = overview_service.generate_overview(repo)

    assert result["overview"]
    assert len(result["modules"]) >= 1
    # one generate call per module (map) + one reduce
    assert fake.models.calls == len(result["modules"]) + 1
    assert all(m["summary"] for m in result["modules"])


def test_generate_overview_is_cached(tmp_path, monkeypatch):
    repo = _tiny_repo(tmp_path)
    graph_service.clear_graph_cache()
    overview_service.clear_overview_cache()

    fake = _FakeClient()
    monkeypatch.setattr(overview_service, "_get_client", lambda: fake)

    overview_service.generate_overview(repo)
    first_calls = fake.models.calls
    overview_service.generate_overview(repo)  # cached -> no new calls

    assert fake.models.calls == first_calls


def test_generate_overview_empty_repo(tmp_path, monkeypatch):
    graph_service.clear_graph_cache()
    overview_service.clear_overview_cache()
    fake = _FakeClient()
    monkeypatch.setattr(overview_service, "_get_client", lambda: fake)

    result = overview_service.generate_overview(str(tmp_path))

    assert result["modules"] == []
    assert fake.models.calls == 0
    assert "No analysable source files" in result["overview"]
