import os
import sys
import json
import io
from urllib import error
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import api_client


class DummyResponse:
    def __init__(self, data: bytes):
        self._data = data

    def read(self):
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass


def test_ask_handles_http_error(monkeypatch):
    def fake_urlopen(req, timeout=10):
        raise error.HTTPError(req.full_url, 500, "error", {}, io.BytesIO(b"Oops"))

    monkeypatch.setattr(api_client.request, "urlopen", fake_urlopen)

    cfg = {"base_url": "http://example", "model": "m", "api_key": "k"}
    with pytest.raises(RuntimeError) as excinfo:
        api_client.ask("hi", cfg)
    assert str(excinfo.value) == "HTTP 500: Oops"


def test_ask_handles_url_error(monkeypatch):
    def fake_urlopen(req, timeout=10):
        raise error.URLError("timeout")

    monkeypatch.setattr(api_client.request, "urlopen", fake_urlopen)

    cfg = {"base_url": "http://example", "model": "m"}
    with pytest.raises(RuntimeError) as excinfo:
        api_client.ask("hi", cfg)
    assert str(excinfo.value) == "Request failed: timeout"


def test_ask_parses_json_response(monkeypatch):
    resp_json = json.dumps({"choices": [{"message": {"content": "result"}}]})

    def fake_urlopen(req, timeout=10):
        return DummyResponse(resp_json.encode("utf-8"))

    monkeypatch.setattr(api_client.request, "urlopen", fake_urlopen)

    cfg = {"base_url": "http://example", "model": "m"}
    result = api_client.ask("hi", cfg)
    assert result == "result"
