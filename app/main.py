from flask import Flask, request, jsonify
import json
import os

from . import api_client, memory

app = Flask(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')

if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as fh:
        CONFIG = json.load(fh)
else:
    CONFIG = {}


@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json(force=True)
    user = data.get('user')
    message = data.get('message')
    if not user or not message:
        return jsonify({'error': 'Missing user or message'}), 400
    response_text = api_client.ask(message, CONFIG)
    try:
        memory.save_interaction(user, message, response_text)
    except Exception:
        pass  # Ignore memory errors
    return jsonify({'response': response_text})


if __name__ == '__main__':
    app.run()
