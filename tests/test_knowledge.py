import os
import sys
import json
import io
import types
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Provide minimal werkzeug stubs when the real package is unavailable
if 'werkzeug' not in sys.modules:
    werkzeug = types.ModuleType('werkzeug')
    datastructures = types.ModuleType('werkzeug.datastructures')
    utils = types.ModuleType('werkzeug.utils')

    class FileStorage:
        def __init__(self, stream=None, filename=None):
            self.stream = stream
            self.filename = filename

        def save(self, dst):
            self.stream.seek(0)
            with open(dst, 'wb') as fh:
                fh.write(self.stream.read())

    def secure_filename(name: str) -> str:  # noqa: D401 - simple stub
        return os.path.basename(name)

    datastructures.FileStorage = FileStorage
    utils.secure_filename = secure_filename
    werkzeug.datastructures = datastructures
    werkzeug.utils = utils
    sys.modules['werkzeug'] = werkzeug
    sys.modules['werkzeug.datastructures'] = datastructures
    sys.modules['werkzeug.utils'] = utils

from werkzeug.datastructures import FileStorage

from app import knowledge


def _setup_paths(tmp_path, monkeypatch):
    root = tmp_path / "kn"
    entries = root / "entries.jsonl"
    monkeypatch.setattr(knowledge, "KNOWLEDGE_DIR", str(root))
    monkeypatch.setattr(knowledge, "FILES_DIR", str(root / "files"))
    monkeypatch.setattr(knowledge, "ENTRIES_FILE", str(entries))
    return entries


def test_add_entry_with_text_and_search(tmp_path, monkeypatch):
    entries = _setup_paths(tmp_path, monkeypatch)

    knowledge.add_entry("Doc1", "Some comment", text="Hello world")

    assert entries.is_file()
    line = entries.read_text(encoding="utf-8").strip()
    entry = json.loads(line)
    assert entry["title"] == "Doc1"
    assert entry["comment"] == "Some comment"
    assert entry["text"] == "Hello world"

    by_title = knowledge.search_entries("Doc1")
    by_comment = knowledge.search_entries("Some comment")
    assert any(e.get("title") == "Doc1" for e in by_title)
    assert any(e.get("title") == "Doc1" for e in by_comment)


def test_add_entry_with_file_and_search(tmp_path, monkeypatch):
    entries = _setup_paths(tmp_path, monkeypatch)

    data = io.BytesIO(b"file content")
    fs = FileStorage(stream=data, filename="info.txt")
    knowledge.add_entry("FileTitle", "File comment", file=fs)

    line = entries.read_text(encoding="utf-8").strip()
    entry = json.loads(line)
    assert entry["title"] == "FileTitle"
    assert entry["comment"] == "File comment"
    assert "path" in entry
    saved_path = tmp_path / "kn" / entry["path"]
    assert saved_path.is_file()

    by_title = knowledge.search_entries("FileTitle")
    by_comment = knowledge.search_entries("File comment")
    assert any(e.get("path") == entry["path"] for e in by_title)
    assert any(e.get("path") == entry["path"] for e in by_comment)


def test_add_entry_requires_text_or_file(tmp_path, monkeypatch):
    entries = _setup_paths(tmp_path, monkeypatch)

    with pytest.raises(ValueError):
        knowledge.add_entry("Empty", "No content")

    assert not entries.exists()


def test_search_entries_respects_limit(tmp_path, monkeypatch):
    entries = _setup_paths(tmp_path, monkeypatch)

    for i in range(3):
        knowledge.add_entry(f"Doc{i}", "Same comment", text="foo")

    results = knowledge.search_entries("Same comment", limit=1)
    assert len(results) == 1
    assert results[0]["title"] == "Doc0"


def test_search_entries_custom_limit(tmp_path, monkeypatch):
    """search_entries should not return more than the requested limit."""
    _setup_paths(tmp_path, monkeypatch)

    for i in range(2):
        knowledge.add_entry(f"LimitDoc{i}", "Limit comment", text="foo")

    results = knowledge.search_entries("Limit comment", limit=1)
    assert len(results) <= 1


def test_add_entry_with_category_and_search(tmp_path, monkeypatch):
    entries = _setup_paths(tmp_path, monkeypatch)

    data = io.BytesIO(b"content")
    fs = FileStorage(stream=data, filename="manual.pdf")
    knowledge.add_entry(
        "Manual", "Manual comment", file=fs, category="manuals"
    )

    line = entries.read_text(encoding="utf-8").strip()
    entry = json.loads(line)
    assert entry["category"] == "manuals"
    assert entry["path"].startswith("files/manuals/")
    saved_path = tmp_path / "kn" / entry["path"]
    assert saved_path.is_file()

    results = knowledge.search_entries("Manual", category="manuals")
    assert any(e.get("path") == entry["path"] for e in results)


def test_search_entries_filter_by_category(tmp_path, monkeypatch):
    _setup_paths(tmp_path, monkeypatch)

    knowledge.add_entry("A", "same", text="foo", category="c1")
    knowledge.add_entry("B", "same", text="foo", category="c2")

    all_results = knowledge.search_entries("same")
    assert len(all_results) == 2

    c1_results = knowledge.search_entries("same", category="c1")
    assert len(c1_results) == 1
    assert c1_results[0]["category"] == "c1"

