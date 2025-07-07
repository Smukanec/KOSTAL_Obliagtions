import os
import re
import sys
import json
import builtins
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

from app import memory


def test_save_interaction_sanitizes_user(tmp_path, monkeypatch):
    root = tmp_path / "mem"
    monkeypatch.setattr(memory, "MEMORY_ROOT", str(root))
    monkeypatch.setattr(memory, "KNOWLEDGE_LOG", os.path.join(str(root), "knowledge_additions.jsonl"))

    user = "bob/../../evil"
    memory.save_interaction(user, "hi", "hello")

    sanitized = re.sub(r"[^A-Za-z0-9_]+", "", user)
    expected_file = root / sanitized / "private.jsonl"
    assert expected_file.is_file()
    # Ensure the file is within the configured memory root
    assert root.resolve() in expected_file.resolve().parents


def test_log_knowledge_addition_writes_comment(tmp_path, monkeypatch):
    root = tmp_path / "mem"
    log_path = root / "knowledge_additions.jsonl"
    monkeypatch.setattr(memory, "MEMORY_ROOT", str(root))
    monkeypatch.setattr(memory, "KNOWLEDGE_LOG", str(log_path))

    memory.log_knowledge_addition("My Title", "Some comment")

    assert log_path.is_file()
    line = log_path.read_text(encoding="utf-8").strip()
    entry = json.loads(line)
    assert entry["title"] == "My Title"
    assert entry["comment"] == "Some comment"


def test_load_interactions_parses_entries(tmp_path, monkeypatch):
    root = tmp_path / "mem"
    monkeypatch.setattr(memory, "MEMORY_ROOT", str(root))
    monkeypatch.setattr(memory, "KNOWLEDGE_LOG", os.path.join(str(root), "knowledge_additions.jsonl"))

    user = "alice/../../secret"
    sanitized = re.sub(r"[^A-Za-z0-9_]+", "", user)
    log_path = root / sanitized
    log_path.mkdir(parents=True)
    file = log_path / "private.jsonl"
    entries = [
        {"timestamp": "t1", "user": "hi", "bot": "hello"},
        {"timestamp": "t2", "user": "hey", "bot": "hi"},
    ]
    with open(file, "w", encoding="utf-8") as fh:
        for e in entries:
            fh.write(json.dumps(e) + "\n")
        fh.write("bad json\n")

    loaded = memory.load_interactions(user)
    assert loaded == entries


def test_load_interactions_missing_file(tmp_path, monkeypatch):
    root = tmp_path / "mem"
    monkeypatch.setattr(memory, "MEMORY_ROOT", str(root))
    monkeypatch.setattr(memory, "KNOWLEDGE_LOG", os.path.join(str(root), "knowledge_additions.jsonl"))

    loaded = memory.load_interactions("nosuchuser")
    assert loaded == []


def test_save_interaction_logs_error(tmp_path, monkeypatch, capsys):
    root = tmp_path / "mem"
    monkeypatch.setattr(memory, "MEMORY_ROOT", str(root))
    monkeypatch.setattr(memory, "KNOWLEDGE_LOG", os.path.join(str(root), "knowledge_additions.jsonl"))

    def bad_open(*args, **kwargs):
        raise OSError("boom")

    monkeypatch.setattr(builtins, "open", bad_open)

    memory.save_interaction("bob", "hi", "there")

    captured = capsys.readouterr()
    assert "boom" in captured.err.lower()
