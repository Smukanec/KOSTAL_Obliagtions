import os
import sys
import json
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Provide minimal werkzeug stubs when the real package is unavailable
if "werkzeug" not in sys.modules:
    werkzeug = types.ModuleType("werkzeug")
    datastructures = types.ModuleType("werkzeug.datastructures")
    utils = types.ModuleType("werkzeug.utils")

    class FileStorage:
        def __init__(self, stream=None, filename=None):
            self.stream = stream
            self.filename = filename

        def save(self, dst):
            self.stream.seek(0)
            with open(dst, "wb") as fh:
                fh.write(self.stream.read())

    def secure_filename(name: str) -> str:
        return os.path.basename(name)

    datastructures.FileStorage = FileStorage
    utils.secure_filename = secure_filename
    werkzeug.datastructures = datastructures
    werkzeug.utils = utils
    sys.modules["werkzeug"] = werkzeug
    sys.modules["werkzeug.datastructures"] = datastructures
    sys.modules["werkzeug.utils"] = utils


# Provide minimal Flask stubs when the real package is unavailable
if 'flask' not in sys.modules:
    flask = types.ModuleType('flask')

    class Response:
        def __init__(self, data=b'', status=200):
            self.data = data if isinstance(data, (bytes, bytearray)) else data.encode('utf-8')
            self.status_code = status
            self.headers = {}

    class Flask:
        def __init__(self, name, static_folder=None):
            self.static_folder = static_folder
            self.response_class = Response

        def route(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

        def send_static_file(self, filename):
            path = os.path.join(self.static_folder, filename)
            with open(path, 'rb') as fh:
                data = fh.read()
            return Response(data, 200)

    def jsonify(obj):
        return Response(json.dumps(obj).encode('utf-8'), 200)

    flask.Flask = Flask
    flask.request = types.SimpleNamespace(get_json=lambda *a, **k: {}, form={}, files={}, authorization=None, method='GET')
    flask.jsonify = jsonify
    sys.modules['flask'] = flask


from importlib import import_module, reload

def _reload_app(monkeypatch, config_path):
    monkeypatch.setenv("ADMIN_PASS", "secret")
    main = import_module("app.main")
    reload(main)
    monkeypatch.setattr(main, "CONFIG_PATH", str(config_path))
    main.CONFIGS = {}
    return main


def _set_request(monkeypatch, main_mod, method='GET', password=None, json_data=None):
    auth = types.SimpleNamespace(password=password) if password is not None else None
    data = json_data or {}
    req = types.SimpleNamespace(
        authorization=auth,
        method=method,
        headers={},
        files={},
        form={},
        get_json=lambda *a, **k: data if method == 'POST' else data,
    )
    monkeypatch.setattr(sys.modules['flask'], 'request', req, raising=False)
    if main_mod is not None:
        monkeypatch.setattr(main_mod, 'request', req, raising=False)


# --- Tests ---

def test_admin_page_auth(monkeypatch, tmp_path):
    cfg = tmp_path / 'cfg.json'
    cfg.write_text('{}', encoding='utf-8')
    main = _reload_app(monkeypatch, cfg)

    _set_request(monkeypatch, main, method='GET')
    resp = main.admin_page()
    assert resp.status_code == 401

    _set_request(monkeypatch, main, method='GET', password='secret')
    resp = main.admin_page()
    assert resp.status_code == 200
    admin_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'admin.html')
    with open(admin_path, 'rb') as fh:
        expected = fh.read()
    assert resp.data == expected


def test_admin_config_get(monkeypatch, tmp_path):
    cfg = tmp_path / 'cfg.json'
    cfg.write_text('{"a":1}', encoding='utf-8')
    main = _reload_app(monkeypatch, cfg)

    _set_request(monkeypatch, main, method='GET')
    resp, status = main.admin_config()
    assert status == 401

    _set_request(monkeypatch, main, method='GET', password='secret')
    resp = main.admin_config()
    assert resp.status_code == 200
    returned = json.loads(resp.data.decode('utf-8'))
    with open(cfg, 'r', encoding='utf-8') as fh:
        assert returned['config'] == fh.read()


def test_admin_config_post(monkeypatch, tmp_path):
    cfg = tmp_path / 'cfg.json'
    cfg.write_text('{}', encoding='utf-8')
    main = _reload_app(monkeypatch, cfg)

    data = {'config': '{"b":2}'}
    _set_request(monkeypatch, main, method='POST', json_data=data)
    resp, status = main.admin_config()
    assert status == 401

    data['password'] = 'secret'
    _set_request(monkeypatch, main, method='POST', json_data=data)
    resp = main.admin_config()
    assert resp.status_code == 200
    result = json.loads(resp.data.decode('utf-8'))
    assert result['status'] == 'ok'
    saved = json.load(open(cfg, 'r', encoding='utf-8'))
    assert saved == {'b': 2}

