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

---------------------------------------------------------------------------------------------------------
# Interactive Document QA System (RAG + Feedback Loop)

This system enables intelligent question answering over your custom documents using Retrieval-Augmented Generation (RAG), with an integrated feedback loop for continuous improvement.

---

## 1. 📄 Document Ingestion & Vectorstore Creation

**Purpose:**  
To make your documents searchable and usable for Q&A.

**How it works:**
- Upload documents (`.pdf`, `.docx`, `.txt`, `.md`, `.csv`) via the Streamlit app (`chat_rag.py`).
- The app:
  - Splits each document into chunks.
  - Embeds them using **OpenAI embeddings**.
  - Stores them in a **Chroma vectorstore** (`vectorstore_nomic`).
- Original files can be deleted after processing — content is now indexed and searchable.

---

## 2. ❓ Question Answering (RAG) via Streamlit

**Purpose:**  
To answer user questions using both document retrieval and an LLM.

**How it works:**
- Users input questions in the Streamlit UI.
- The app:
  - Retrieves relevant chunks from the **Chroma vectorstore**.
  - Sends the question and retrieved chunks to an **OpenAI LLM** via **LangChain**.
- The LLM generates and returns an answer.
- The response includes the **answer** and the **source documents** used.

---

## 3. 📝 Feedback Collection

**Purpose:**  
To gather user feedback on answer quality for continuous improvement.

**How it works:**
- After each answer, users can give a 👍 or 👎 and optionally leave a comment.
- Feedback is saved in `feedback_log.jsonl` as:
  - Question
  - Answer
  - Sources
  - Feedback type
  - Comment (optional)

---

## 4. 🛠️ Automated Feedback Analysis & Pipeline Improvement

**Purpose:**  
To analyze user feedback for improving system accuracy and reliability.

**How it works:**
- The `analyze_feedback.py` script:
  - Parses `feedback_log.jsonl`.
  - Finds most downvoted questions.
  - Identifies source documents commonly associated with poor answers.
  - Collects user comments on downvoted responses.
  - Flags problematic documents (≥3 downvotes) in `sources_to_review.txt`.
  - Creates `llm_finetune_data.jsonl` — a dataset for possible LLM fine-tuning.

---

## 5. 🎯 (Optional) LLM Fine-Tuning

**Purpose:**  
To enhance LLM performance on your specific domain/questions.

**How it works:**
- The `llm_finetune_data.jsonl` file includes:
  - Questions
  - Answers
  - Context (source chunks)
  - Feedback metadata
  - User comments
- You can use this dataset to fine-tune an LLM, given access to a fine-tuning API or infrastructure.

---

## 🚀 Tech Stack

- **Streamlit** – User interface
- **LangChain** – Orchestrates retrieval and LLM calls
- **OpenAI API** – Embeddings and LLM
- **ChromaDB** – Vector store for document chunks
- **JSONL Logs** – Feedback storage and analysis

---

## 📂 Project Files Overview

| File | Description |
|------|-------------|
| `chat_rag.py` | Streamlit app for document upload and Q&A |
| `analyze_feedback.py` | Analyzes feedback and prepares data for fine-tuning |
| `feedback_log.jsonl` | Stores user feedback |
| `llm_finetune_data.jsonl` | Dataset generated from feedback |
| `sources_to_review.txt` | Problematic sources flagged for manual review |

---

## ✅ Next Steps

- Add support for multi-model selection (e.g., OpenAI, Ollama).
- Visualize feedback analytics in the UI.
- Add export/share options for chat and answers.
- Integrate admin tools to manage sources and fine-tuning.

---

Built with ❤️ for human-in-the-loop document intelligence.
