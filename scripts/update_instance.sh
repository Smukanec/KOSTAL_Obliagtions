#!/bin/bash
set -e

# Stop any running Flask server on port 5000
if command -v lsof >/dev/null; then
    pids=$(lsof -t -i:5000) || true
    if [ -n "$pids" ]; then
        kill -9 $pids || true
    fi
else
    fuser -k 5000/tcp || true
fi

# Backup memory folder
TS=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="memory_backup/$TS"
mkdir -p "$BACKUP_DIR"
if [ -d memory ]; then
    cp -r memory/* "$BACKUP_DIR" 2>/dev/null || true
fi

# Pull latest changes
git pull

# Install dependencies
pip install -r requirements.txt

# Restart Flask server
nohup python3 app/main.py > flask.log 2>&1 &

echo "Server restarted."
