from backend.analyzer.scanner import scan_repo


def test_scan_repo_finds_supported_and_skips_ignored(tmp_path):
    (tmp_path / "app.py").write_text("x = 1\n")
    (tmp_path / "ui.jsx").write_text("export const A = 1;\n")
    (tmp_path / "notes.txt").write_text("ignore me\n")

    vendored = tmp_path / "node_modules" / "pkg"
    vendored.mkdir(parents=True)
    (vendored / "index.js").write_text("module.exports = {};\n")

    files = scan_repo(str(tmp_path))
    names = {f.name for f in files}

    assert names == {"app.py", "ui.jsx"}


def test_scan_repo_populates_fileinfo(tmp_path):
    (tmp_path / "app.py").write_text("x = 1\n")

    (file,) = scan_repo(str(tmp_path))

    assert file.name == "app.py"
    assert file.extension == ".py"
    assert file.path == str((tmp_path / "app.py").resolve())
    assert file.module_name
