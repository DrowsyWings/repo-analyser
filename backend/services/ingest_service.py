import shutil
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_HOSTS = {"github.com", "www.github.com"}

DOWNLOAD_TIMEOUT = 30  # seconds
MAX_ARCHIVE_BYTES = 50 * 1024 * 1024  # compressed download cap
MAX_EXTRACTED_BYTES = 200 * 1024 * 1024  # uncompressed cap (tar-bomb guard)
MAX_FILES = 10_000

_CHUNK = 64 * 1024


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


def _stream_with_cap(source, dest: Path) -> None:
    downloaded = 0
    with open(dest, "wb") as out:
        while True:
            chunk = source.read(_CHUNK)
            if not chunk:
                break
            downloaded += len(chunk)
            if downloaded > MAX_ARCHIVE_BYTES:
                raise RepoDownloadError("Repository archive exceeds the size limit.")
            out.write(chunk)


def _extract_with_limits(archive: Path, dest: Path) -> None:
    with tarfile.open(archive, "r:gz") as tar:
        files = [m for m in tar.getmembers() if m.isreg()]
        if len(files) > MAX_FILES:
            raise RepoDownloadError(f"Repository has too many files (> {MAX_FILES}).")
        if sum(m.size for m in files) > MAX_EXTRACTED_BYTES:
            raise RepoDownloadError("Repository exceeds the extracted-size limit.")
        tar.extractall(dest, filter="data")


def download_github_repo(repo_url: str) -> Path:
    owner, repo = parse_github_repo(repo_url)
    tarball_url = f"https://api.github.com/repos/{owner}/{repo}/tarball"

    tmp_dir = Path(tempfile.mkdtemp(prefix="repo-analyze-"))
    archive = tmp_dir / "repo.tar.gz"

    try:
        request = urllib.request.Request(
            tarball_url, headers={"User-Agent": "repo-analyze"}
        )
        try:
            with urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT) as response:
                _stream_with_cap(response, archive)
        except (urllib.error.URLError, TimeoutError) as exc:
            raise RepoDownloadError(
                f"Failed to download {owner}/{repo}: {exc}"
            ) from exc

        _extract_with_limits(archive, tmp_dir)
        archive.unlink()

        extracted = [p for p in tmp_dir.iterdir() if p.is_dir()]
        if not extracted:
            raise RepoDownloadError(
                "Downloaded archive contained no repository directory."
            )
        return extracted[0]
    except Exception:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise
