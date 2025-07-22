#!/bin/bash

# Create SSL directory if it doesn't exist
mkdir -p ssl

# Generate self-signed SSL certificate if it doesn't exist
if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
  echo "Generating self-signed SSL certificate..."
  openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem -out ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
  echo "SSL certificate generated."
fi

# Stop and remove existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.local.cpu.yml down

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating sample .env file..."
  echo "# Add your API keys below" > .env
  echo "OPENAI_API_KEY=your-openai-key" >> .env
  echo "GEMINI_API_KEY=your-gemini-key" >> .env
  echo "Created .env file. Please edit it with your actual API keys."
fi

# Start the application
echo "Starting Freightify Bot with HTTPS..."
docker-compose -f docker-compose.local.cpu.yml up -d --build

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
echo "Access it at: https://$IP/freightify/"
echo ""
echo "NOTE: Since we're using a self-signed certificate, you'll need to accept the security warning in your browser."
echo ""
echo "To check logs: docker-compose -f docker-compose.local.cpu.yml logs -f"
echo "To stop: docker-compose -f docker-compose.local.cpu.yml down"