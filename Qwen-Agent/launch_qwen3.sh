#!/bin/bash

# Change to the script's directory
cd "$(dirname "$0")"

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama..."
    ollama serve &
    sleep 5  # Wait for Ollama to start
fi

# Pull qwen3 model if not already present
echo "Ensuring qwen3 model is available..."
ollama pull qwen3

# Kill any existing webui processes
pkill -f "python.*webui.py"

# Start the web UI
echo "Starting Qwen3 Agent Builder..."
python webui.py
