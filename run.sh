#!/bin/bash

# ===================================
# Before running this script, do:
# Make it executable
# chmod +x run.sh (from the root dir)

# Then run this script:
# ./run.sh
# ===================================

# Ensure PostgreSQL is running (before running fastapi app)
if ! systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL service..."
    sudo systemctl start postgresql
    sleep 3
else
    echo "PostgreSQL already running."
fi

# Run FastAPI app
echo "Starting FastAPI app..."
uv run fastapi dev app/main.py --port 8083
