from backend.services import embedding_service


class _FakeEmbedding:
    def __init__(self, values):
        self.values = values


class _FakeResponse:
    def __init__(self, embeddings):
        self.embeddings = embeddings


class _FakeModels:
    def __init__(self):
        self.calls = []

    def embed_content(self, model, contents, config):
        self.calls.append((model, list(contents), config.task_type))
        return _FakeResponse([_FakeEmbedding([float(len(c))]) for c in contents])


class _FakeClient:
    def __init__(self):
        self.models = _FakeModels()


def test_embed_documents_batches(monkeypatch):
    fake = _FakeClient()
    monkeypatch.setattr(embedding_service, "_get_client", lambda: fake)
    monkeypatch.setattr(embedding_service, "BATCH_SIZE", 2)

    vectors = embedding_service.embed_documents(["a", "bb", "ccc", "dddd", "e"])

    assert len(vectors) == 5
    assert len(fake.models.calls) == 3  # ceil(5 / 2) batches
    assert fake.models.calls[0][2] == "RETRIEVAL_DOCUMENT"


def test_embed_query_uses_query_task_type(monkeypatch):
    fake = _FakeClient()
    monkeypatch.setattr(embedding_service, "_get_client", lambda: fake)

    vector = embedding_service.embed_query("hello")

    assert vector == [5.0]
    assert fake.models.calls[0][2] == "RETRIEVAL_QUERY"


def test_embed_documents_empty_makes_no_call(monkeypatch):
    fake = _FakeClient()
    monkeypatch.setattr(embedding_service, "_get_client", lambda: fake)

    assert embedding_service.embed_documents([]) == []
    assert fake.models.calls == []
