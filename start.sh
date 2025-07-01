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

# Start the Flask server
nohup python3 app/main.py > flask.log 2>&1 &

echo "Server started."
