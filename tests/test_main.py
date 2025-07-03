import os
import sys
import json
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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


def test_index_serves_ui(monkeypatch):
    monkeypatch.setenv('ADMIN_PASS', 'x')
    from importlib import reload
    import app.main as main
    reload(main)

    resp = main.index()
    assert resp.status_code == 200
    ui_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'ui.html')
    with open(ui_path, 'rb') as fh:
        expected = fh.read()
    assert resp.data == expected
