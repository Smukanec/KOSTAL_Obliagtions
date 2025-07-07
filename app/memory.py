"""Simple JSONL-based conversation memory."""

import json
import os
import re
import sys
from datetime import datetime

MEMORY_ROOT = os.path.join(os.path.dirname(__file__), '..', 'memory')
KNOWLEDGE_LOG = os.path.join(MEMORY_ROOT, 'knowledge_additions.jsonl')


def save_interaction(user: str, user_message: str, bot_message: str) -> None:
    """Append a conversation entry for given user."""
    # Sanitize user string to avoid directory traversal
    user = re.sub(r"[^A-Za-z0-9_]+", "", user)
    user_dir = os.path.join(MEMORY_ROOT, user)
    os.makedirs(user_dir, exist_ok=True)
    log_file = os.path.join(user_dir, 'private.jsonl')
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'user': user_message,
        'bot': bot_message,
    }
    try:
        with open(log_file, 'a', encoding='utf-8') as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception as exc:  # noqa: BLE001 - log then ignore
        print(f"Failed to save interaction: {exc}", file=sys.stderr)


def load_interactions(user: str) -> list:
    """Return list of conversation entries for given user."""
    # Sanitize user string to avoid directory traversal
    user = re.sub(r"[^A-Za-z0-9_]+", "", user)
    log_file = os.path.join(MEMORY_ROOT, user, 'private.jsonl')
    if not os.path.exists(log_file):
        return []

    entries = []
    with open(log_file, 'r', encoding='utf-8') as fh:
        for line in fh:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def log_knowledge_addition(title: str, comment: str) -> None:
    """Log a knowledge entry creation."""
    os.makedirs(MEMORY_ROOT, exist_ok=True)
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'title': title,
        'comment': comment,
    }
    with open(KNOWLEDGE_LOG, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + '\n')
