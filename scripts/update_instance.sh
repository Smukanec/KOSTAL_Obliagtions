#!/bin/bash
set -e

# Stop any running Flask server on port 5000
pids=""
if command -v lsof >/dev/null; then
    pids=$(lsof -t -i:5000 2>/dev/null) || true
elif command -v fuser >/dev/null; then
    pids=$(fuser 5000/tcp 2>/dev/null | sed 's/.*://; s/^ *//') || true
elif command -v netstat >/dev/null; then
    pids=$(netstat -lntp 2>/dev/null | awk '$4 ~ /:5000$/ && $6 == "LISTEN" {split($7,a,"/"); print a[1]}') || true
else
    echo "Warning: no tool available to detect processes on port 5000" >&2
fi

if [ -n "$pids" ]; then
    kill -9 $pids || true
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
