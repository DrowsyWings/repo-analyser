import pytest

from backend.services.ingest_service import RepoDownloadError, parse_github_repo


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
