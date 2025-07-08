# 🧠 Interactive CrewAI: Document Analysis

This project allows users to interactively choose:
- A **Document Summarizer Agent**
- A **Test Case Generator Agent**

Each agent works on documents in the `common/` folder.

## 🚀 How to Run

### 1. Install Poetry (if not already installed)
```bash
curl -sSL https://install.python-poetry.org | python3 -


### if using Ubuntu or WSL, you may need extra system deps for unstructured:
sudo apt install poppler-utils tesseract-ocr

# 🧠 CrewAI Document Analyzer with RAG + Chroma

This project uses [CrewAI](https://github.com/joaomdmoura/crewai) to create autonomous agents that:
- Summarize internal documentation based on user queries
- Generate test case scenarios from workflows described in your docs

Now enhanced with a **Retrieval-Augmented Generation (RAG)** pipeline using **Chroma vector DB** for context-aware responses!

---
## 🔧 Features
✅ Agent selection at runtime  
✅ Reads from `.md`, `.txt`, `.pdf`, `.docx`, `.csv`, `.xlsx`  
✅ Embeds documents into Chroma once  
✅ Retrieves only relevant chunks at runtime  
✅ Generates high-quality LLM responses with embedded context
---

## 🗂️ Folder Structure
doc_analysis_crew/
├── .env # OpenAI API key
├── pyproject.toml # Poetry dependencies
├── README.md
├── common/ # Place all source documents here
├── scripts/
│ └── embed_docs.py # Script to embed and persist docs to vector DB
└── src/
└── doc_analysis/
├── agents.py # CrewAI agents
├── tasks.py # CrewAI tasks
├── main.py # Runtime interface
└── tools/
├── db_logger.py
└── rag_vector_tool.py

yaml
---
## 🚀 Quick Start
### 1️⃣ Install dependencies
```bash
poetry install


2️⃣ Set your OpenAI API Key
Create a file called .env in the root:

3️⃣ Add your documents
Place .txt, .md, .pdf, .docx, .csv, .xlsx files in the common/ folder.
mkdir common
# Copy in your documents

4️⃣ Run the document embedding script
This will:
** Load & chunk your files
** Embed the chunks using OpenAI
** Store them in a local Chroma vector store

## Run this command

poetry run python scripts/embed_docs.py
----
You should see the following:
✅ Vector store created with 68 chunks.
----

5️⃣ Run the main agent app
poetry run python src/doc_analysis/main.py

# Choose which agent to run:
Choose an agent to run:
1. Document Summarizer
2. Test Case Generator
3. API Test Generator

#Then input your query:
Summarize the onboarding workflow for contractors

The agent will:
Embed the query
Fetch top relevant document chunks
Send to LLM with query
Return final output

For memory usage inspection
--------
poetry run python scripts/inspect_logs.py

Will return the following along with logs (vector store & sqlite)

"""
✅ Total Chunks: 36
🧠 Total Characters in Top 5 Chunks: 3362

💾 Storage Usage:
--------------------------------------------------
📦 Chroma Vector Store: 123644.70 KB
🗃️ SQLite Log DB: 8.00 KB
"""

5️⃣ Run the unittest 
-- poetry run python -m unittest.{{filename}} > this will test the function logic

💡 Notes
All queries/responses are logged to SQLite via db_logger.py

📦 Tech Stack
CrewAI
LangChain
ChromaDB
OpenAI
Unstructured