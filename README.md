# JARVIK KOSTAL GPT PROXY

Tento projekt je odlehčená verze Jarvika, navržená pro běh v prostředí bez možnosti instalace modelů. Dotazy jsou směrovány na firemní API **KOSTAL GPT** (přes LangChain `ChatOpenAI`).

## 🔧 Požadavky
- Python 3.9+
- `pip install flask langchain openai`

## 📁 Struktura
```
jarvik-kostal/
├── app/
│   ├── main.py            # Flask backend
│   ├── api_client.py      # Volání KOSTAL GPT
│   └── memory.py          # Jednoduchá paměť v JSONL
│
├── config/
│   └── config.json        # API klíč + model + endpoint
│
├── memory/                # Historie dotazů podle uživatele
│   └── jiri/private.jsonl
│
├── static/                # (volitelné UI)
│   └── ui.html
│
├── requirements.txt
└── README.md
```

## 🚀 Spuštění
```bash
export FLASK_APP=app/main.py
flask run
```
Nebo jednoduše:
```bash
python3 app/main.py
```
## 🔄 Update
Pro aktualizaci serveru spusť:
```bash
bash scripts/update_instance.sh
```


## 🧠 Endpoint `/ask`
```json
POST /ask
{
  "user": "jiri",
  "message": "Jak funguje solární měnič?"
}
```
Odpověď:
```json
{
  "response": "Solární měnič převádí..."
}
```

## 🔑 Konfigurace API
V souboru `config/config.json` nastav:
```json
{
  "api_key": "sk-...",
  "base_url": "https://gpt-api.kostal.com",
  "model": "azure-gpt-4o"
}
```

## 🗃️ Paměť
Konverzace se ukládají jako JSONL:
```jsonl
{"timestamp": ..., "user": "Ahoj", "bot": "Dobrý den"}
```

## 📎 Poznámky
- Neobsahuje RAG vrstvu
- Nepoužívá Ollamu ani lokální modely
- Vhodné pro interní firemní použití (KOSTAL)

---

Pokud chceš přidat UI (`ui.html`), stačí otevřít `/static/ui.html` nebo připojit route v `Flask`.
