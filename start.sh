#!/bin/bash
set -e

# Detect available Python interpreter
PYTHON=$(command -v python3 || command -v python || command -v py)
if [ -z "$PYTHON" ]; then
    echo "Python interpreter not found." >&2
    exit 1
fi

# Ensure admin password is provided
if [ -z "$ADMIN_PASS" ]; then
    echo "ADMIN_PASS not defined – set it before running" >&2
    exit 1
fi

# Use provided port or default to 5000
PORT=${PORT:-5000}
export PORT

# Determine the directory this script lives in and switch to the
# repository root so relative paths work regardless of where the
# script is invoked from.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/.."

# Stop any running Flask server on port $PORT
pids=""
if command -v lsof >/dev/null; then
    pids=$(lsof -t -i:"$PORT" 2>/dev/null) || true
elif command -v fuser >/dev/null; then
    pids=$(fuser "$PORT"/tcp 2>/dev/null | sed 's/.*://; s/^ *//') || true
elif command -v netstat >/dev/null; then
    pids=$(netstat -lntp 2>/dev/null | awk -v p=":$PORT$" '$4 ~ p && $6 == "LISTEN" {split($7,a,"/"); print a[1]}') || true
else
    echo "Warning: no tool available to detect processes on port $PORT" >&2
fi

if [ -n "$pids" ]; then
    kill -9 $pids || true
fi

# Start the Flask server on the chosen port
nohup "$PYTHON" app/main.py > flask.log 2>&1 &

echo "Server started."
