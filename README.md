# JARVIK KOSTAL GPT PROXY

Tento projekt je odlehčená verze Jarvika, navržená pro běh v prostředí bez možnosti instalace modelů. Dotazy jsou směrovány na firemní API **KOSTAL GPT** (přes LangChain `ChatOpenAI`).

## 🔧 Požadavky
- Python 3.9+
- `pip install flask langchain openai`

## Windows notes
Scripts expect an executable named `python3`. If that command isn't available
on Windows you can either add Python to your `PATH` or create an alias in your
`~/.bashrc`:

```bash
alias python3='/c/Path/To/python.exe'
```

The startup scripts now try `python`, `python3` or `py` in this order, so as
long as one of these commands exists the server will launch correctly.

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

## 💻 Webové UI
Po spuštění serveru otevři v prohlížeči `http://localhost:5000/`.
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
Heslo pro přístup se nastavuje proměnnou prostředí `ADMIN_PASS`
(výchozí hodnota `Kostal@2025` je určena jen pro lokální testování).
Pro ověření se používá HTTP Basic Auth nebo odeslání hesla v těle POST
požadavku. Rozhraní umožňuje měnit API klíče i model a je určeno pouze
pro interní použití. Příklad načtení konfigurace pomocí `curl`:
```bash
curl -u admin:$ADMIN_PASS http://localhost:5000/admin/config
```
