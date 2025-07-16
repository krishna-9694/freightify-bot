import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH", "vectorstore_nomic")
USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"

def get_embeddings():
    if USE_OLLAMA:
        print("🔁 Using Ollama embeddings")
        return OllamaEmbeddings(model="nomic-embed-text")
    else:
        print("🔁 Using OpenAI embeddings")
        return OpenAIEmbeddings()

def main():
    embedding_fn = get_embeddings()

    print("📚 Loading vector store...")
    vectordb = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embedding_fn,
    )

    while True:
        query = input("🔍 Enter your question (or type 'exit'): ").strip()
        if query.lower() == "exit":
            break

        results = vectordb.similarity_search(query, k=3)
        print("\n📄 Top results:")
        for i, doc in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(doc.page_content)
            print(f"[Source: {doc.metadata.get('filename', 'unknown')}]")

if __name__ == "__main__":
    main()
