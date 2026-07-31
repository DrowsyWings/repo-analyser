from backend.analyzer.chunker import Chunk
from backend.services import vector_store


def _use_temp_store(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_store, "CHROMA_DIR", tmp_path / "chroma")
    monkeypatch.setattr(vector_store, "_client", None)


def _chunks():
    return [
        Chunk("a.py", "alpha", "function", 1, 3, "def alpha(): pass"),
        Chunk("b.py", "beta", "function", 1, 3, "def beta(): return 2"),
    ]


def test_build_and_query_returns_nearest(tmp_path, monkeypatch):
    _use_temp_store(tmp_path, monkeypatch)
    repo = "owner/repo@sha1"

    assert vector_store.has_index(repo) is False

    vector_store.build_index(repo, _chunks(), [[1.0, 0.0], [0.0, 1.0]])

    assert vector_store.has_index(repo) is True

    hits = vector_store.query(repo, [1.0, 0.0], k=1)
    assert len(hits) == 1
    assert hits[0]["metadata"]["path"] == "a.py"
    assert hits[0]["metadata"]["name"] == "alpha"


def test_build_index_replaces_previous(tmp_path, monkeypatch):
    _use_temp_store(tmp_path, monkeypatch)
    repo = "owner/repo@sha1"

    vector_store.build_index(repo, _chunks(), [[1.0, 0.0], [0.0, 1.0]])
    single = [Chunk("c.py", "gamma", "function", 1, 2, "def gamma(): pass")]
    vector_store.build_index(repo, single, [[0.5, 0.5]])

    hits = vector_store.query(repo, [0.5, 0.5], k=5)
    assert len(hits) == 1
    assert hits[0]["metadata"]["path"] == "c.py"


def test_persistence_across_clients(tmp_path, monkeypatch):
    _use_temp_store(tmp_path, monkeypatch)
    repo = "owner/repo@sha1"
    vector_store.build_index(repo, _chunks(), [[1.0, 0.0], [0.0, 1.0]])

    # drop the in-process client; a fresh one must read the persisted index
    monkeypatch.setattr(vector_store, "_client", None)
    assert vector_store.has_index(repo) is True
