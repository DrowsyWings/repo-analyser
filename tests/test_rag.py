from backend.services import rag_service, vector_store


class _FakeResponse:
    def __init__(self, text):
        self.text = text


class _FakeStreamChunk:
    def __init__(self, text):
        self.text = text


class _FakeModels:
    def __init__(self):
        self.prompts = []

    def generate_content(self, model, contents):
        self.prompts.append(contents)
        return _FakeResponse("GENERATED ANSWER")

    def generate_content_stream(self, model, contents):
        self.prompts.append(contents)
        return iter([_FakeStreamChunk("Hello "), _FakeStreamChunk("world")])


class _FakeClient:
    def __init__(self):
        self.models = _FakeModels()


_HITS = [
    {
        "content": "def login(): ...",
        "metadata": {
            "path": "auth.py",
            "name": "login",
            "start_line": 10,
            "end_line": 20,
        },
    },
    {
        "content": "def login(): ...",  # duplicate span -> deduped in citations
        "metadata": {
            "path": "auth.py",
            "name": "login",
            "start_line": 10,
            "end_line": 20,
        },
    },
]


def test_answer_question_builds_prompt_and_cites(monkeypatch):
    fake = _FakeClient()
    monkeypatch.setattr(rag_service, "ensure_index", lambda repo_path: None)
    monkeypatch.setattr(vector_store, "has_index", lambda repo_path: True)
    monkeypatch.setattr(rag_service, "retrieve", lambda repo_path, q, k=5: _HITS)
    monkeypatch.setattr(rag_service, "_get_client", lambda: fake)

    result = rag_service.answer_question("/repo", "where is login handled?")

    assert result["answer"] == "GENERATED ANSWER"
    assert result["citations"] == [
        {"path": "auth.py", "name": "login", "start_line": 10, "end_line": 20}
    ]
    assert "def login()" in fake.models.prompts[0]
    assert "where is login handled?" in fake.models.prompts[0]


def test_retrieve_expands_with_graph_neighbors(monkeypatch):
    semantic = [
        {
            "content": "def handler(): ...",
            "metadata": {
                "path": "api.py",
                "name": "handler",
                "start_line": 1,
                "end_line": 5,
            },
        }
    ]
    neighbor = [
        {
            "content": "def helper(): ...",
            "metadata": {
                "path": "utils.py",
                "name": "helper",
                "start_line": 1,
                "end_line": 3,
            },
        }
    ]
    graph = {
        "nodes": [
            {"id": "api", "path": "api.py"},
            {"id": "utils", "path": "utils.py"},
        ],
        "edges": [{"source": "api", "target": "utils"}],
    }

    monkeypatch.setattr(rag_service, "embed_query", lambda q: [1.0, 0.0])
    monkeypatch.setattr(vector_store, "query", lambda repo, vec, k=5: semantic)
    monkeypatch.setattr(rag_service, "get_graph", lambda repo_path: graph)
    monkeypatch.setattr(
        vector_store,
        "get_file_chunks",
        lambda repo, paths: neighbor if paths == ["utils.py"] else [],
    )

    hits = rag_service.retrieve("/repo", "how does the handler work?")
    paths = [h["metadata"]["path"] for h in hits]
    assert paths == ["api.py", "utils.py"]  # semantic hit + import neighbor


def test_answer_question_no_source_files(monkeypatch):
    monkeypatch.setattr(rag_service, "ensure_index", lambda repo_path: None)
    monkeypatch.setattr(vector_store, "has_index", lambda repo_path: False)

    result = rag_service.answer_question("/repo", "anything?")

    assert result["citations"] == []
    assert "No analysable source files" in result["answer"]


def test_stream_answer_yields_tokens_then_done(monkeypatch):
    fake = _FakeClient()
    monkeypatch.setattr(rag_service, "ensure_index", lambda repo_path: None)
    monkeypatch.setattr(vector_store, "has_index", lambda repo_path: True)
    monkeypatch.setattr(rag_service, "retrieve", lambda repo_path, q, k=5: _HITS)
    monkeypatch.setattr(rag_service, "_get_client", lambda: fake)

    events = list(rag_service.stream_answer("/repo", "q"))

    assert [e["type"] for e in events] == ["token", "token", "done"]
    answer = "".join(e["text"] for e in events if e["type"] == "token")
    assert answer == "Hello world"
    assert events[-1]["citations"] == [
        {"path": "auth.py", "name": "login", "start_line": 10, "end_line": 20}
    ]


def test_stream_answer_no_source_files(monkeypatch):
    monkeypatch.setattr(rag_service, "ensure_index", lambda repo_path: None)
    monkeypatch.setattr(vector_store, "has_index", lambda repo_path: False)

    events = list(rag_service.stream_answer("/repo", "q"))

    assert events[0]["type"] == "token"
    assert events[-1] == {"type": "done", "citations": []}


def test_ensure_index_builds_from_repo(tmp_path, monkeypatch):
    (tmp_path / "mod.py").write_text("def alpha():\n    return 1\n")
    (tmp_path / "util.py").write_text("def beta():\n    return 2\n")

    monkeypatch.setattr(vector_store, "CHROMA_DIR", tmp_path / "chroma")
    monkeypatch.setattr(vector_store, "_client", None)
    monkeypatch.setattr(
        rag_service,
        "embed_documents",
        lambda texts: [[float(i + 1), 0.0] for i in range(len(texts))],
    )

    repo = str(tmp_path)
    assert vector_store.has_index(repo) is False
    rag_service.ensure_index(repo)
    assert vector_store.has_index(repo) is True

    # second call is a no-op (index already present) — would raise if it embedded
    monkeypatch.setattr(
        rag_service,
        "embed_documents",
        lambda texts: (_ for _ in ()).throw(AssertionError("should not re-embed")),
    )
    rag_service.ensure_index(repo)
