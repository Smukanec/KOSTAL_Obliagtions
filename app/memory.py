"""Simple JSONL-based conversation memory."""

import json
import os
from datetime import datetime

MEMORY_ROOT = os.path.join(os.path.dirname(__file__), '..', 'memory')


def save_interaction(user: str, user_message: str, bot_message: str) -> None:
    """Append a conversation entry for given user."""
    user_dir = os.path.join(MEMORY_ROOT, user)
    os.makedirs(user_dir, exist_ok=True)
    log_file = os.path.join(user_dir, 'private.jsonl')
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'user': user_message,
        'bot': bot_message,
    }
    with open(log_file, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + '\n')
