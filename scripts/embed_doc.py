import os
import glob
import ssl
import nltk
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader, CSVLoader
)
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings

ssl._create_default_https_context = ssl._create_unverified_context
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

load_dotenv()

DOC_FOLDER = "common"
MODEL_TYPE = os.getenv("MODEL_TYPE", "openai").lower()

if MODEL_TYPE == "ollama":
    from langchain_community.embeddings import OllamaEmbeddings
    EMBEDDING_MODEL = OllamaEmbeddings(model="nomic-embed-text")
    CHROMA_PATH = "vectorstore_ollama"
    print("🔁 Using Ollama embeddings")
else:
    from langchain_openai import OpenAIEmbeddings
    EMBEDDING_MODEL = OpenAIEmbeddings()
    CHROMA_PATH = "vectorstore_openai"
    print("🔁 Using OpenAI embeddings")

def load_all_documents(folder_path):
    loaders = []
    files = glob.glob(os.path.join(folder_path, "*"))
    for file in files:
        ext = file.lower().split(".")[-1]
        try:
            if ext in ["txt", "md"]:
                loaders.append(TextLoader(file))
            elif ext == "pdf":
                loaders.append(PyPDFLoader(file))
            elif ext in ["docx", "docs"]:
                loaders.append(UnstructuredWordDocumentLoader(file))
            elif ext == "csv":
                loaders.append(CSVLoader(file))
            elif ext == "xlsx":
                loaders.append(UnstructuredExcelLoader(file))
        except Exception as e:
            print(f"⚠️ Skipping {file}: {e}")
    docs = []
    for loader in loaders:
        for doc in loader.load():
            doc.metadata["source"] = loader.file_path
            doc.metadata["filename"] = os.path.basename(loader.file_path)
            docs.append(doc)
    return docs

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_documents(documents)

def embed_and_store(docs):
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=EMBEDDING_MODEL,
        persist_directory=CHROMA_PATH
    )
    print(f"✅ Vector store created at `{CHROMA_PATH}` with {len(docs)} chunks.")

if __name__ == "__main__":
    print(f"📂 Loading documents from `{DOC_FOLDER}`...")
    raw_docs = load_all_documents(DOC_FOLDER)
    print(f"📄 Loaded {len(raw_docs)} documents")
    print("✂️ Splitting into chunks...")
    chunks = split_documents(raw_docs)
    print(f"🔍 Total chunks: {len(chunks)}")
    print("📦 Embedding and storing in ChromaDB...")
    embed_and_store(chunks)
