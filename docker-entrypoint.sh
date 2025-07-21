#!/bin/bash

# Wait for Ollama service to be ready
echo "Waiting for Ollama service..."
until curl -s http://ollama:11434/api/version > /dev/null; do
  sleep 1
done
echo "Ollama service is ready!"

# Pull required models
echo "Pulling Ollama models..."
curl -X POST http://ollama:11434/api/pull -d '{"name": "nomic-embed-text"}'
curl -X POST http://ollama:11434/api/pull -d '{"name": "llama3"}'
echo "Models pulled successfully!"

# Start Streamlit
echo "Starting Streamlit application..."
streamlit run scripts/chat_rag.py --server.address=0.0.0.0