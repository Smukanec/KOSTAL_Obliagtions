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
    response_text = api_client.ask(message, CONFIG)
    related = knowledge.search_entries(message)
    if related:
        titles = [e.get('title') for e in related]
        response_text += "\n\nReferences:\n" + "\n".join(titles)
    try:
        memory.save_interaction(user, message, response_text)
    except Exception:
        pass  # Ignore memory errors
    return jsonify({'response': response_text})


@app.route('/knowledge/add', methods=['POST'])
def add_knowledge():
    title = request.form.get('title')
    comment = request.form.get('comment', '')
    text = request.form.get('text', '')
    file = request.files.get('file')
    if not title:
        return jsonify({'error': 'Missing title'}), 400
    entry = knowledge.add_entry(title, comment, text, file)
    try:
        memory.log_knowledge_addition(entry['title'])
    except Exception:
        pass
    return jsonify({'status': 'ok', 'entry': entry})


if __name__ == '__main__':
    app.run()
