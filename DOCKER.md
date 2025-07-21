# Docker Setup for Freightify Bot

This guide explains how to run Freightify Bot using Docker for consistent deployment across different environments.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Setup Instructions

### 1. Configure Environment Variables

Create a `.env` file in the project root with your API keys:

```
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key

# Optional: Qdrant configuration (if using)
QDRANT_API_KEY=your-qdrant-api-key
QDRANT_URL=https://your-cluster.qdrant.io
```

### 2. Add Documents (Optional)

Place any documents you want pre-loaded in the `common/` folder.

### 3. Build and Run with Docker Compose

**With GPU support (if available):**
```bash
docker-compose up -d
```

**CPU-only version:**
```bash
docker-compose -f docker-compose.cpu.yml up -d
```

This will:
- Build the Docker image
- Start the Ollama service container
- Start the Freightify Bot container
- Map port 8501 to your host for the web interface
- Mount necessary volumes for data persistence

### 4. Access the Application

Open your browser and navigate to:
```
http://localhost:8501
```

## Data Persistence

The following directories are mounted as volumes to ensure data persistence:

- `./common`: Pre-loaded documents
- `./uploads`: User-uploaded documents
- `./faiss_index_openai`: Vector indices for OpenAI embeddings
- `./faiss_index_ollama`: Vector indices for Ollama embeddings (if used locally)

## Stopping the Application

```bash
docker-compose down
```

## Rebuilding After Code Changes

```bash
docker-compose up -d --build
```

## Notes

- The setup includes an Ollama service that runs in a separate container
- GPU acceleration is configured if available on your host machine
- The entrypoint script automatically pulls the required Ollama models (nomic-embed-text, llama3)
- You can use both OpenAI and Ollama models for embeddings and inference

## Using GPU Acceleration

If you have an NVIDIA GPU and want to use it with Ollama:

1. Install NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html

2. Verify your GPU is detected:
```bash
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

3. The docker-compose.yml is already configured to use all available GPUs

## Troubleshooting

If you encounter issues with Ollama:

1. Check if the Ollama service is running:
```bash
docker-compose logs ollama
```

2. You can manually pull models if needed:
```bash
docker-compose exec ollama ollama pull nomic-embed-text
docker-compose exec ollama ollama pull llama3
```