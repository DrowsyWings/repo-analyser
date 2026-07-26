import io
import tarfile

import pytest

from backend.services import ingest_service
from backend.services.ingest_service import RepoDownloadError, parse_github_repo


def _make_tar(path, files):
    with tarfile.open(path, "w:gz") as tar:
        for name, content in files.items():
            data = content.encode()
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/octocat/Hello-World",
        "https://github.com/octocat/Hello-World/",
        "https://github.com/octocat/Hello-World.git",
        "https://github.com/octocat/Hello-World/tree/main",
    ],
)
def test_parse_github_repo_accepts_valid_urls(url):
    assert parse_github_repo(url) == ("octocat", "Hello-World")


@pytest.mark.parametrize(
    "url",
    [
        "https://gitlab.com/octocat/Hello-World",
        "https://example.com/octocat/Hello-World",
        "https://github.com/octocat",
    ],
)
def test_parse_github_repo_rejects_invalid_urls(url):
    with pytest.raises(RepoDownloadError):
        parse_github_repo(url)


def test_stream_with_cap_rejects_oversize(tmp_path, monkeypatch):
    monkeypatch.setattr(ingest_service, "MAX_ARCHIVE_BYTES", 4)
    with pytest.raises(RepoDownloadError):
        ingest_service._stream_with_cap(io.BytesIO(b"123456789"), tmp_path / "f.bin")


def test_stream_with_cap_writes_content(tmp_path):
    dest = tmp_path / "f.bin"
    ingest_service._stream_with_cap(io.BytesIO(b"hello"), dest)
    assert dest.read_bytes() == b"hello"


def test_extract_with_limits_rejects_too_many_files(tmp_path, monkeypatch):
    archive = tmp_path / "a.tar.gz"
    _make_tar(archive, {"repo/a.py": "x", "repo/b.py": "y"})
    monkeypatch.setattr(ingest_service, "MAX_FILES", 1)
    dest = tmp_path / "out"
    dest.mkdir()
    with pytest.raises(RepoDownloadError):
        ingest_service._extract_with_limits(archive, dest)


def test_extract_with_limits_extracts_files(tmp_path):
    archive = tmp_path / "a.tar.gz"
    _make_tar(archive, {"repo/a.py": "print(1)\n"})
    dest = tmp_path / "out"
    dest.mkdir()
    ingest_service._extract_with_limits(archive, dest)
    assert (dest / "repo" / "a.py").read_text() == "print(1)\n"


def test_download_reuses_cached_commit(tmp_path, monkeypatch):
    repo_dir = tmp_path / "octocat-Hello-World-abc123"
    repo_dir.mkdir()

    ingest_service.clear_download_cache()
    monkeypatch.setattr(ingest_service, "_resolve_sha", lambda owner, repo: "abc123")
    ingest_service._download_cache["octocat/Hello-World@abc123"] = repo_dir

    def _boom(owner, repo):
        raise AssertionError("should not re-download a cached commit")

    monkeypatch.setattr(ingest_service, "_fetch_and_extract", _boom)

    result = ingest_service.download_github_repo(
        "https://github.com/octocat/Hello-World"
    )
    assert result == repo_dir
    ingest_service.clear_download_cache()


def test_iter_download_steps_emits_progress(tmp_path, monkeypatch):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    ingest_service.clear_download_cache()
    monkeypatch.setattr(ingest_service, "_resolve_sha", lambda owner, repo: "sha1")
    monkeypatch.setattr(
        ingest_service, "_fetch_and_extract", lambda owner, repo: repo_dir
    )

    steps = ingest_service.iter_download_steps("https://github.com/octocat/Hello-World")
    stages = []
    path = None
    try:
        while True:
            stage, _ = next(steps)
            stages.append(stage)
    except StopIteration as stop:
        path = stop.value

    assert stages == ["resolving", "downloading"]
    assert path == repo_dir
    ingest_service.clear_download_cache()
