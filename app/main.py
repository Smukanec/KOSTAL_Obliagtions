from flask import Flask, request, jsonify, send_from_directory
import json
import os

from . import api_client, memory, knowledge

app = Flask(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as fh:
        raw_cfg = json.load(fh)
    if isinstance(raw_cfg, list):
        CONFIGS = {c.get('name', str(i)): c for i, c in enumerate(raw_cfg)}
    elif isinstance(raw_cfg, dict) and 'api_key' in raw_cfg:
        CONFIGS = {'default': raw_cfg}
    else:
        CONFIGS = raw_cfg
else:
    CONFIGS = {}


@app.route('/')
def index():
    """Serve the simple UI."""
    return app.send_static_file('ui.html')


@app.route('/configs')
def get_configs():
    """Return available configurations without API keys."""
    sanitized = {}
    for name, cfg in CONFIGS.items():
        sanitized[name] = {k: v for k, v in cfg.items() if k != 'api_key'}
    return jsonify(sanitized)


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json(force=True)
    user = data.get('user')
    message = data.get('message')
    cfg_name = data.get('config')
    if not user or not message:
        return jsonify({'error': 'Missing user or message'}), 400
    related = knowledge.search_entries(message)
    cfg = CONFIGS.get(cfg_name)
    if cfg is None and CONFIGS:
        cfg = next(iter(CONFIGS.values()))
    response_text = api_client.ask(message, cfg or {})
    try:
        memory.save_interaction(user, message, response_text)
    except Exception:
        pass  # Ignore memory errors
    return jsonify({'response': response_text, 'references': [e['title'] for e in related]})


@app.route('/knowledge/add', methods=['POST'])
def add_knowledge():
    title = request.form.get('title')
    comment = request.form.get('comment', '')
    text = request.form.get('text')
    file_obj = request.files.get('file')
    if not title:
        return jsonify({'error': 'Missing title'}), 400
    if not text and file_obj is None:
        return jsonify({'error': 'Provide text or file'}), 400
    try:
        knowledge.add_entry(title, comment, text=text, file=file_obj)
        memory.log_knowledge_addition(title)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run()
