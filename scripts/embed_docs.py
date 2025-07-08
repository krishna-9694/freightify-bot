import os
import glob
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    CSVLoader
)
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = "vectorstore"

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
        docs.extend(loader.load())

    return docs

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)

def embed_and_store(docs):
    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(),
        persist_directory="vectorstore"
    )
    vectordb.persist()
    print(f"✅ Vector store created with {len(docs)} chunks.")

if __name__ == "__main__":
    raw_docs = load_all_documents("common")
    chunks = split_documents(raw_docs)
    embed_and_store(chunks)
