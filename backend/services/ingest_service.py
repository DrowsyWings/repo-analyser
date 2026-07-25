import shutil
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_HOSTS = {"github.com", "www.github.com"}


class RepoDownloadError(Exception):
    pass


def parse_github_repo(repo_url: str) -> tuple[str, str]:
    parsed = urlparse(repo_url.strip())

    if parsed.netloc.lower() not in ALLOWED_HOSTS:
        raise RepoDownloadError("Only github.com repository URLs are supported.")

    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise RepoDownloadError(
            "URL must point to a repository: https://github.com/<owner>/<repo>."
        )

    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo


def download_github_repo(repo_url: str) -> Path:
    owner, repo = parse_github_repo(repo_url)
    tarball_url = f"https://api.github.com/repos/{owner}/{repo}/tarball"

    tmp_dir = Path(tempfile.mkdtemp(prefix="repo-analyze-"))
    archive = tmp_dir / "repo.tar.gz"

    request = urllib.request.Request(
        tarball_url, headers={"User-Agent": "repo-analyze"}
    )
    try:
        with urllib.request.urlopen(request) as response, open(archive, "wb") as out:
            shutil.copyfileobj(response, out)
    except urllib.error.URLError as exc:
        raise RepoDownloadError(f"Failed to download {owner}/{repo}: {exc}") from exc

    with tarfile.open(archive, "r:gz") as tar:
        tar.extractall(tmp_dir, filter="data")

    archive.unlink()

    extracted = [p for p in tmp_dir.iterdir() if p.is_dir()]
    if not extracted:
        raise RepoDownloadError("Downloaded archive contained no repository directory.")
    return extracted[0]
