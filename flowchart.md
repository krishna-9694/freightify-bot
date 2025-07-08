                        ┌────────────────────────────────────────────┐
                        │             🗃 common/ Folder               │
                        │ .md, .txt, .pdf, .csv, .docx, .xlsx, etc.  │
                        └────────────────────────────────────────────┘
                                       │
                          (1) Load & Chunk Documents
                                       │
                                       ▼
                          ┌───────────────────────────┐
                          │    embed_docs.py script   │
                          │ - Uses LangChain loaders  │
                          │ - Splits docs into chunks │
                          └───────────────────────────┘
                                       │
                          (2) Embed chunks using OpenAI
                                       │
                                       ▼
                            ┌────────────────────────┐
                            │   Chroma Vector Store  │
                            │   (persisted to disk)  │
                            └────────────────────────┘
                                       ▲
                          (3) Load on demand by tool
                                       │
                         ┌──────────────────────────────┐
                         │ 🔧 RAG Tool (rag_vector_tool) │
                         │ - Embeds incoming query       │
                         │ - Searches Chroma             │
                         │ - Returns top-K text chunks   │
                         └──────────────────────────────┘
                                       │
                          (4) Inject chunks into prompt
                                       │
                                       ▼
                  ┌────────────────────────────────────────────┐
                  │          🤖 CrewAI Agent                    │
                  │--------------------------------------------│
                  │ Document Summarizer or Test Generator       │
                  │ - Receives query + relevant doc context    │
                  │ - Calls OpenAI LLM                         │
                  │ - Produces final response                  │
                  └────────────────────────────────────────────┘
                                       │
                          (5) Log output to SQLite DB
                                       ▼
                          ┌────────────────────────┐
                          │    db_logger Tool      │
                          └────────────────────────┘
