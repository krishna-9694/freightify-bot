# 🚢 Freightify Bot: Document Intelligence System

A powerful document analysis and question-answering system built with CrewAI, LangChain, and Qdrant vector database. This system provides intelligent responses to queries about your documents with multi-agent analysis capabilities.

## ✨ Features

- **Conversational Chat Interface**: User-friendly Streamlit UI with message history
- **Multi-Agent Analysis**: Collaborative AI agents for comprehensive document analysis
- **Multiple LLM Support**: Works with OpenAI, Gemini, and Ollama models
- **Scalable Vector Storage**: Qdrant integration for handling large document collections
- **Document Processing**: Support for PDF, DOCX, TXT, MD, CSV, and XLSX files
- **External Integrations**: Connect with Jira, Freshworks, and Google Drive
- **Feedback Collection**: Gather user feedback to improve responses over time

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Framework**: CrewAI + LangChain
- **Vector Database**: Qdrant (with FAISS fallback)
- **LLM Providers**: OpenAI, Google Gemini, Ollama
- **Document Processing**: Unstructured, PyPDF, python-docx

## 📋 Prerequisites

- Python 3.10+
- Poetry (recommended) or pip
- API keys for LLM providers (OpenAI, Gemini)
- Qdrant cloud account or local installation (optional)

## 🚀 Quick Start (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/krishna-9694/freightify-bot.git
cd freightify-bot
```

### 2. Install Dependencies

**Using Poetry (recommended)**:
```bash
# Install Poetry if you don't have it
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
```

**Using pip**:
```bash
pip install -e .
```

### 3. Set Up Environment Variables

```bash
# Copy the sample environment file
cp sampleenv .env

# Edit .env with your API keys
# Required:
# - OPENAI_API_KEY (for OpenAI models)
# - GEMINI_API_KEY (for Google Gemini models)
# 
# Optional for Qdrant cloud:
# - QDRANT_API_KEY
# - QDRANT_URL
#
# Optional for local Qdrant:
# - QDRANT_PATH=./qdrant_data
```

### 4. Create Required Directories

```bash
mkdir -p common uploads faiss_index_openai faiss_index_ollama
```

### 5. Add Your Documents

Place your documents in the `common/` folder:
```bash
# Copy your documents to the common folder
cp your-documents/*.pdf common/
cp your-documents/*.docx common/
```

### 6. Run the Application

```bash
# Using Poetry
poetry run streamlit run scripts/chat_rag.py

# Using Python directly
streamlit run scripts/chat_rag.py
```

## 🧠 Using the Application

1. **Select Models**: Choose embedding and retrieval models in the sidebar
2. **Upload Documents**: Use the upload button to add documents to the system
3. **Choose Agent Mode**:
   - **Standard Chat**: Basic question-answering
   - **Multi-Agent Analysis**: Comprehensive analysis with multiple perspectives
   - **Learning Enhanced**: Adaptive responses based on previous interactions
4. **Ask Questions**: Type your questions in the chat input
5. **View Sources**: Expand the "Source Documents" section to see where information came from
6. **Provide Feedback**: Rate responses with 👍 or 👎 to help improve the system

## 🔌 Integrations

### Jira Integration
Connect to Jira to fetch and analyze issues:
1. Enter your Jira URL, email, and API token
2. Optionally specify a ticket number or fetch recent issues
3. Click "Fetch Jira Issues"

### Freshworks Integration
Connect to Freshworks to analyze support tickets:
1. Enter your Freshworks domain and API key
2. Optionally specify a ticket ID
3. Click "Fetch Freshworks Tickets"

### Google Drive Integration
Connect to Google Drive to analyze documents:
1. Choose authentication method (API Key or OAuth)
2. Select document retrieval method (Document ID, Folder ID, or Recent Documents)
3. Click "Fetch Google Documents"

## 🧹 Repository Maintenance

To clean up temporary files and prepare for deployment:

```bash
# Run the cleanup script
python scripts/cleanup_repo.py
```

## ☁️ Cloud Deployment

The application is designed to work in cloud environments like Streamlit Cloud:

1. **Automatic Fallbacks**: In cloud environments, the app automatically:
   - Uses OpenAI embeddings instead of Ollama
   - Uses FAISS instead of Qdrant for vector storage
   - Provides appropriate error messages and fallbacks

2. **Required Environment Variables**:
   - `OPENAI_API_KEY`: Required for embeddings and OpenAI models
   - `GEMINI_API_KEY`: Required if using Gemini models

3. **Deploy to Streamlit Cloud**:
   - Connect your GitHub repository to Streamlit Cloud
   - Set the required environment variables
   - Set the main file to `scripts/chat_rag.py`

## 📊 Advanced Features

### Vector Database Migration

If you need to migrate from FAISS to Qdrant:

```bash
python scripts/migrate_to_qdrant.py
```

### Feedback Analysis

Analyze user feedback to improve the system:

```bash
python scripts/analyze_feedback.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.