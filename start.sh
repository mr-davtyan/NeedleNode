#!/bin/bash
# start.sh

# Ensure uv is in path for virtualenv
export PATH="$HOME/.local/bin:$PATH"

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv .venv
    uv pip install -r backend/requirements.txt
fi

source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.

# Kill existing if any
if [ -f .server.pid ]; then
    ./stop.sh > /dev/null 2>&1
fi

echo "Starting Embroidery Manager on http://localhost:8000..."
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
echo $! > .server.pid

echo "Server started in background. Logs saved to server.log"
echo "To view logs: tail -f server.log"
echo "To stop server: ./stop.sh"
