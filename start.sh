#!/bin/bash

# Create necessary directories
mkdir -p common uploads faiss_index_openai faiss_index_ollama

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating sample .env file..."
  echo "# Add your API keys below" > .env
  echo "OPENAI_API_KEY=your-openai-key" >> .env
  echo "GEMINI_API_KEY=your-gemini-key" >> .env
  echo "Created .env file. Please edit it with your actual API keys."
fi

# Start the application
echo "Starting Freightify Bot..."
docker-compose -f docker-compose.local.cpu.yml up -d

# Get the IP address
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1)
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  IP=$(hostname -I | awk '{print $1}')
else
  # Windows or other
  IP="localhost"
fi

echo ""
echo "Freightify Bot is starting up!"
echo "Access it at: http://$IP/freightify"
echo ""
echo "To check logs: docker-compose -f docker-compose.local.cpu.yml logs -f"
echo "To stop: docker-compose -f docker-compose.local.cpu.yml down"