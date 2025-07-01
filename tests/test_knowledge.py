import os
import sys
import json
import io
import types

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
