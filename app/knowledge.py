import json
import os
import re
import time
from datetime import datetime
from typing import List, Optional
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), '..', 'knowledge')
FILES_DIR = os.path.join(KNOWLEDGE_DIR, 'files')
ENTRIES_FILE = os.path.join(KNOWLEDGE_DIR, 'entries.jsonl')


def _ensure_dirs() -> None:
    os.makedirs(KNOWLEDGE_DIR, exist_ok=True)
    os.makedirs(FILES_DIR, exist_ok=True)


def add_entry(
    title: str,
    comment: str,
    text: Optional[str] = None,
    file: Optional[FileStorage] = None,
    category: Optional[str] = None,
) -> None:
    """Store a knowledge entry with optional text or uploaded file."""
    if not text and not file:
        raise ValueError('Either text or file must be provided')

    _ensure_dirs()
    if category:
        category = re.sub(r"[^A-Za-z0-9_]+", "", category)
        os.makedirs(os.path.join(FILES_DIR, category), exist_ok=True)
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'title': title,
        'comment': comment,
        **({'category': category} if category else {}),
    }
    if file is not None:
        filename = f"{int(time.time())}_{secure_filename(file.filename)}"
        target_dir = FILES_DIR
        if category:
            target_dir = os.path.join(FILES_DIR, category)
        path = os.path.join(target_dir, filename)
        file.save(path)
        parts = ['files'] + ([category] if category else []) + [filename]
        entry['path'] = os.path.join(*parts)
    else:
        entry['text'] = text

    with open(ENTRIES_FILE, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + '\n')


def search_entries(
    query: str,
    limit: int = 3,
    category: Optional[str] = None,
) -> List[dict]:
    """Return knowledge entries with query string in title or comment."""
    if not os.path.exists(ENTRIES_FILE):
        return []
    if category:
        category = re.sub(r"[^A-Za-z0-9_]+", "", category)
    q = query.lower()
    results = []
    with open(ENTRIES_FILE, 'r', encoding='utf-8') as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if category and entry.get('category') != category:
                continue
            text = (entry.get('title', '') + ' ' + entry.get('comment', '')).lower()
            if q in text:
                results.append(entry)
                if len(results) >= limit:
                    break
    return results
