# Deployment Guide

## Prerequisites
- Python 3.10+
- Poetry
- OpenAI API Key
- (Optional) Ollama for local models

## Environment Setup

1. Copy sample environment file:
```bash
cp sampleenv .env
```

2. Configure required variables:
```bash
OPENAI_API_KEY=your_openai_key
MODEL_TYPE=openai  # or ollama
```

## Installation

1. Install dependencies:
```bash
poetry install
```

2. Embed documents:
```bash
poetry run python scripts/embed_doc.py
```

3. Run the application:
```bash
poetry run python src/doc_analysis/main.py
```

## Streamlit Interface

```bash
poetry run streamlit run scripts/chat_rag.py
```

## Docker Deployment (Recommended)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install
CMD ["poetry", "run", "streamlit", "run", "scripts/chat_rag.py"]
```