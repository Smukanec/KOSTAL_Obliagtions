# JARVIK KOSTAL GPT PROXY

Tento projekt je odlehčená verze Jarvika, navržená pro běh v prostředí bez možnosti instalace modelů. Dotazy jsou směrovány na firemní API **KOSTAL GPT** (přes LangChain `ChatOpenAI`).

## 🔧 Požadavky
- Python 3.9+
- `pip install flask langchain openai`

## Windows notes
The batch scripts search for `python`, `python3` or `py` and use the first one
found. Ensure at least one of these commands is available in your `PATH` so the
server can start correctly.

See [docs/windows-http-setup.md](docs/windows-http-setup.md) for a detailed Windows setup.

## Creating a virtual environment
To keep dependencies isolated you can create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
```

Before running `python app/main.py` make sure the environment variable `ADMIN_PASS` is set.

### Starting on Windows
Use `start.bat` from the project root to launch the server. If you created a
virtual environment, activate it first:

```cmd
call venv\Scripts\activate.bat
start.bat
```

The batch file stops any process already listening on the port defined by
the `PORT` variable (default `80`) and runs the
Flask app in the current window. Stop it with `Ctrl+C` or by closing the
terminal. Run `start.bat` again or `scripts\update_instance.bat` to restart the
server.
Binding to ports below 1024 may require running the script as Administrator.
For an update and automatic restart use `scripts\update_instance.bat`. It pulls
the latest code, installs dependencies and then starts the server again.

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
export ADMIN_PASS=mojeheslo
flask run
```
Nebo jednoduše (nezapomeň nastavit heslo):
```bash
export ADMIN_PASS=mojeheslo
python3 app/main.py
```

## 💻 Webové UI
Po spuštění serveru otevři v prohlížeči `http://localhost:$PORT/`.
Výchozí port je `80` a lze jej změnit proměnnou prostředí `PORT` (např. `PORT=443`).
Při použití portů pod 1024 může být nutné spustit server s administrátorskými právy.
Zobrazí se jednoduché rozhraní, kde zvolíš konfigurační profil,
zadáš otázku a uvidíš odpověď i použitý kontext.
V sekci "Add Knowledge" můžeš nahrát text nebo soubor s komentářem.

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

## 📚 Knowledge Base
Struktura adresáře pro znalosti:
```
knowledge/
├── entries.jsonl  # seznam všech záznamů
└── files/         # uložené soubory
```
Nahrávání probíhá přes webové rozhraní v sekci **Add Knowledge**,
kde vyplníš název, komentář a text nebo soubor. Všechna nahrání se
logují do souboru `memory/knowledge_additions.jsonl`.

Při volání `/ask` se k odpovědi vrací pole `references` obsahující
názvy odpovídajících záznamů.

## 📎 Poznámky
- Neobsahuje RAG vrstvu
- Nepoužívá Ollamu ani lokální modely
- Vhodné pro interní firemní použití (KOSTAL)

---

Webové rozhraní je dostupné na adrese `/` po spuštění serveru.

## 🔐 Admin rozhraní
Konfiguraci v `config/config.json` lze upravit na adrese `/admin`.
Heslo pro přístup se nastavuje proměnnou prostředí `ADMIN_PASS` a
server se nespustí, pokud není proměnná nastavena.
Pro ověření se používá HTTP Basic Auth nebo odeslání hesla v těle POST
požadavku. Rozhraní umožňuje měnit API klíče i model a je určeno pouze
pro interní použití. Příklad načtení konfigurace pomocí `curl`:
```bash
curl -u admin:$ADMIN_PASS http://localhost:$PORT/admin/config
```
