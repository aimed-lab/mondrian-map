#!/bin/bash

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "[ERROR] Streamlit is not installed. Please run: pip install -r config/requirements.txt"
    exit 1
fi

# Function to find an available port
find_available_port() {
    local port=8501
    while lsof -i :$port > /dev/null 2>&1; do
        echo "Port $port is in use, trying next port..."
        port=$((port + 1))
    done
    echo $port
}

# Kill any existing Streamlit processes
echo "Cleaning up any existing Streamlit processes..."
pkill -f streamlit

# Wait a moment for processes to clean up
sleep 2

# Find an available port
PORT=$(find_available_port)
echo "Starting Streamlit on port $PORT"

# Run Streamlit with the available port
streamlit run apps/streamlit_app.py --server.port $PORT --server.address 0.0.0.0 