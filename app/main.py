from flask import Flask, request, jsonify
import json
import os

from . import api_client, memory, knowledge

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
    related = knowledge.search_entries(message)
    response_text = api_client.ask(message, CONFIG)
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
