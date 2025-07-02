"""Simple HTTP client for communicating with the KOSTAL GPT API."""

from typing import Dict
import json
from urllib import request, error


def ask(message: str, config: Dict) -> str:
    """Return response text from the KOSTAL GPT service.

    Parameters
    ----------
    message:
        User provided message which will be sent to the API.
    config:
        Dictionary containing at least ``api_key``, ``base_url`` and ``model``.
    """

    endpoint = config.get("base_url")
    if not endpoint:
        # Without a valid endpoint we can't contact the service, just echo.
        return f"ECHO: {message}"

    payload = {
        "model": config.get("model"),
        "messages": [
            {"role": "user", "content": message},
        ],
    }

    headers = {"Content-Type": "application/json"}
    if config.get("api_key"):
        headers["Authorization"] = f"Bearer {config['api_key']}"

    req = request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=10) as resp:
            resp_data = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        err_text = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"HTTP {exc.code}: {err_text}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Request failed: {exc.reason}") from exc

    try:
        data = json.loads(resp_data)
        return data["choices"][0]["message"]["content"]
    except Exception:  # noqa: BLE001 - return raw text on unexpected format
        return resp_data
