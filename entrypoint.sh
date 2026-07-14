#!/bin/bash

# Start FastAPI backend in the background
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# Wait for a moment to ensure API starts
sleep 3

# Start Streamlit frontend in the foreground
export API_BASE_URL="http://127.0.0.1:8000"
streamlit run src/ui/app.py --server.port 8501 --server.address 0.0.0.0

# If Streamlit exits, kill FastAPI
kill $FASTAPI_PID
