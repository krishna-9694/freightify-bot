FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for unstructured and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    libreoffice \
    curl \
    gnupg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# We'll use the Ollama service instead of installing it in this container
# The container will connect to the Ollama service via HTTP

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create necessary directories
RUN mkdir -p common uploads faiss_index_openai faiss_index_ollama

# Expose the port Streamlit will run on
EXPOSE 8501

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true

# Add entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Command to run the application
CMD ["/app/docker-entrypoint.sh"]