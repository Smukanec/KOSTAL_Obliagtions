from flask import Flask, request, jsonify
import json
import os

from . import api_client, memory, knowledge

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
)

# Password for admin interface
ADMIN_PASS = os.environ.get('ADMIN_PASS')
if not ADMIN_PASS:
    raise SystemExit('ADMIN_PASS environment variable is required')

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
        memory.log_knowledge_addition(title, comment)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
    return jsonify({'status': 'ok'})


# ---- Admin routes ----

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    """Serve admin UI if credentials are valid."""
    password = None
    if request.authorization:
        password = request.authorization.password
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        password = data.get('password', password)
    if password != ADMIN_PASS:
        resp = app.response_class("Unauthorized", 401)
        resp.headers['WWW-Authenticate'] = 'Basic realm="Admin"'
        return resp
    return app.send_static_file('admin.html')


@app.route('/admin/config', methods=['GET', 'POST'])
def admin_config():
    """Return or update full configuration."""
    password = None
    if request.authorization:
        password = request.authorization.password
    if request.method == 'GET':
        if password != ADMIN_PASS:
            return jsonify({'error': 'unauthorized'}), 401
        with open(CONFIG_PATH, 'r', encoding='utf-8') as fh:
            return jsonify({'config': fh.read()})

    data = request.get_json(force=True)
    password = data.get('password', password)
    if password != ADMIN_PASS:
        return jsonify({'error': 'unauthorized'}), 401

    cfg_text = data.get('config')
    if cfg_text is None:
        return jsonify({'error': 'Missing config'}), 400
    try:
        new_cfg = json.loads(cfg_text)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON'}), 400

    with open(CONFIG_PATH, 'w', encoding='utf-8') as fh:
        json.dump(new_cfg, fh, indent=2, ensure_ascii=False)

    global CONFIGS
    if isinstance(new_cfg, list):
        CONFIGS = {c.get('name', str(i)): c for i, c in enumerate(new_cfg)}
    elif isinstance(new_cfg, dict) and 'api_key' in new_cfg:
        CONFIGS = {'default': new_cfg}
    else:
        CONFIGS = new_cfg
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run()
