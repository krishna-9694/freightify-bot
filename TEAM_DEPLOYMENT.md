# Team Deployment Guide

This guide explains how to deploy Freightify Bot with a proper URL for team access.

## Prerequisites

1. A server with Docker and Docker Compose installed
2. A domain name pointing to your server (e.g., freightify-bot.yourdomain.com)

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/krishna-9694/freightify-bot.git
cd freightify-bot
```

### 2. Configure Environment Variables

Create a `.env` file with your API keys:

```
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
```

### 3. Update the Domain Name

Edit the `Caddyfile` to use your actual domain:

```bash
# Replace freightify-bot.yourdomain.com with your actual domain
nano Caddyfile
```

### 4. Deploy with Docker Compose

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### 5. Access the Application

Your team can now access the application at:

```
https://freightify-bot.yourdomain.com
```

Caddy automatically obtains and renews SSL certificates, so you'll have a secure HTTPS connection.

## Maintenance

### Updating the Application

```bash
git pull
docker-compose -f docker-compose.prod.yml up -d --build
```

### Viewing Logs

```bash
# View all logs
docker-compose -f docker-compose.prod.yml logs

# View specific service logs
docker-compose -f docker-compose.prod.yml logs freightify-bot
```

### Stopping the Application

```bash
docker-compose -f docker-compose.prod.yml down
```