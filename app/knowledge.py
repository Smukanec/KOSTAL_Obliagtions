import json
import os
from datetime import datetime
from typing import List, Dict, Optional

KNOWLEDGE_ROOT = os.path.join(os.path.dirname(__file__), '..', 'knowledge')
ENTRIES_FILE = os.path.join(KNOWLEDGE_ROOT, 'entries.jsonl')


def _load_entries() -> List[Dict]:
    if not os.path.exists(ENTRIES_FILE):
        return []
    entries = []
    with open(ENTRIES_FILE, 'r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def add_entry(title: str, comment: str, text: str = '', file_storage: Optional[object] = None) -> Dict:
    """Store a knowledge entry with optional text or uploaded file."""
    os.makedirs(KNOWLEDGE_ROOT, exist_ok=True)
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'title': title,
        'comment': comment,
    }
    if text:
        entry['text'] = text
    if file_storage:
        fname = f"{int(datetime.utcnow().timestamp()*1000)}_{file_storage.filename}"
        fpath = os.path.join(KNOWLEDGE_ROOT, fname)
        file_storage.save(fpath)
        entry['file'] = fname
    with open(ENTRIES_FILE, 'a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + '\n')
    return entry


def search_entries(query: str, limit: int = 3) -> List[Dict]:
    """Return entries where the query text appears in title, comment or text."""
    results: List[Dict] = []
    q = query.lower()
    for entry in _load_entries():
        haystack = ' '.join([
            entry.get('title', ''),
            entry.get('comment', ''),
            entry.get('text', '')
        ]).lower()
        if q in haystack:
            results.append(entry)
        if len(results) >= limit:
            break
    return results
