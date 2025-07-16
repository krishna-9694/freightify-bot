import os
from langchain_chroma import Chroma
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_ollama.llms import OllamaLLM
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

CHROMA_PATH = "vectorstore_nomic"

# Load vectorstore
embedding = OllamaEmbeddings(model="nomic-embed-text")
vectordb = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding)

# Use Ollama LLM (local model)
llm = OllamaLLM(model="llama3")

# Prompt template
template = """Use the context below to answer the question as accurately as possible.
If the answer is not in the context, just say you don’t know — don’t make it up.

Context:
{context}

Question:
{question}
"""
prompt = PromptTemplate(template=template, input_variables=["context", "question"])

# Create RAG chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt}
)

# Interactive loop
print("🧠 Ask a question (type 'exit' to quit):")
while True:
    query = input("🔍 ")
    if query.strip().lower() == "exit":
        break
    answer = qa_chain.invoke({"query": query})  # NEW: `.invoke` instead of `.run`
    print(f"\n🤖 {answer['result']}\n")
