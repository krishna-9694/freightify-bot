import os
import shutil
import streamlit as st
from PIL import Image

from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import (
    PyPDFLoader, UnstructuredWordDocumentLoader, TextLoader, CSVLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Constants ---
CHROMA_PATH = "vectorstore_nomic"
UPLOAD_DIR = "uploads"

# --- Logo and Title ---
logo_path = "scripts/logo.jpg"
st.set_page_config(page_title="Freightify Bot", layout="wide")
col1, col2 = st.columns([8, 1])
with col1:
    st.title("🚢 Freightify Bot - Chat with your Docs")
with col2:
    if os.path.exists(logo_path):
        image = Image.open(logo_path)
        st.image(image, use_container_width=True)

# --- Initialize Embeddings & Vector DB ---
embedding = OllamaEmbeddings(model="nomic-embed-text")
vectordb = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding)

# --- Optional Cleanup and Upload Dir Creation ---
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Helper: Load document based on extension ---
def load_documents_from_path(path):
    ext = path.split(".")[-1].lower()
    if ext == "pdf":
        return PyPDFLoader(path).load()
    elif ext in ["docx", "doc"]:
        return UnstructuredWordDocumentLoader(path).load()
    elif ext == "txt":
        return TextLoader(path).load()
    elif ext == "csv":
        return CSVLoader(path).load()
    return []

# --- Upload and Embed ---
uploaded_files = st.file_uploader(
    "📁 Upload your documents",
    type=["pdf", "docx", "txt", "csv"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("🔄 Processing uploaded files..."):
        all_new_docs = []
        for file in uploaded_files:
            file_path = os.path.join(UPLOAD_DIR, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            docs = load_documents_from_path(file_path)
            all_new_docs.extend(docs)

        # Split and embed
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        new_chunks = splitter.split_documents(all_new_docs)
        vectordb.add_documents(new_chunks)
        st.success(f"✅ Indexed {len(new_chunks)} new chunks from {len(uploaded_files)} file(s)")

# --- QA Chain ---
llm = Ollama(model="llama3")
retriever = vectordb.as_retriever()
qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)

# --- Chat Interface ---
st.markdown("### 💬 Ask a question")
query = st.text_input("🔍 Your question")

if query:
    with st.spinner("🤔 Thinking..."):
        result = qa_chain.invoke({"query": query})
        st.markdown("### 🤖 Answer:")
        st.write(result["result"])

        with st.expander("🧾 Sources"):
            for doc in result["source_documents"]:
                st.markdown(f"**{os.path.basename(doc.metadata.get('source', ''))}**")
                st.write(doc.page_content[:500] + "...")
