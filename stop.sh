#!/bin/bash
# stop.sh

# Check if .server.pid exists
if [ -f .server.pid ]; then
    PID=$(cat .server.pid)
    echo "Stopping server (PID: $PID)..."
    
    # Check if process is still running
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "Server stopped."
    else
        echo "Server is not running (PID $PID is dead)."
    fi
    
    rm .server.pid
else
    # Fallback checking if uvicorn is running
    echo "No .server.pid found. Checking for uvicorn processes..."
    PID=$(pgrep -f "uvicorn backend.main:app")
    if [ ! -z "$PID" ]; then
        echo "Killing uvicorn server (PID: $PID)..."
        kill $PID
        echo "Server stopped."
    else
        echo "No Embroidery Manager processes found running."
    fi
fi
