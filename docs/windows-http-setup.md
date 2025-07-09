# Windows HTTP Setup

This guide describes how to run the Flask server on Windows using
`start.bat`.

## Prerequisites
- Windows with **Python 3.9+** installed.
- Make sure `python`, `python3` or `py` is available in your `PATH` so the
  batch script can locate the interpreter.

## Create and activate a virtual environment
```cmd
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## Environment variables
Set the admin password and optionally the port before launching the
server:
```cmd
set ADMIN_PASS=YourSecretPassword
set PORT=8080  REM optional, defaults to 80
```

## Running the server
From the project root run:
```cmd
start.bat
```
The web UI will then be available at `http://localhost:%PORT%/` (default
`http://localhost:80/`).
