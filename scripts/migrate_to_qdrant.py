#!/usr/bin/env python3
"""
Script to migrate data from FAISS to Qdrant
"""
import os
import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import OllamaEmbeddings

# Add project root to path
sys.path.append('/Users/krishnakumar/projects/AI/jarvis')
from src.doc_analysis.tools.qdrant_store import store_documents

# Load environment variables
load_dotenv()

def migrate_faiss_to_qdrant():
    """Migrate data from FAISS to Qdrant"""
    print("Starting migration from FAISS to Qdrant...")
    
    # Check for OpenAI FAISS index
    if os.path.exists("faiss_index_openai"):
        print("Migrating OpenAI embeddings...")
        embedding_model = OpenAIEmbeddings()
        try:
            # Load FAISS index
            vectordb = FAISS.load_local(
                "faiss_index_openai",
                embeddings=embedding_model,
                allow_dangerous_deserialization=True
            )
            
            # Get all documents
            docs = vectordb.similarity_search("", k=10000)  # Get all docs
            
            # Store in Qdrant
            store_documents(docs, embedding_model, collection_name="freightify_docs_openai")
            print("✅ Successfully migrated OpenAI embeddings to Qdrant")
        except Exception as e:
            print(f"❌ Error migrating OpenAI embeddings: {str(e)}")
    
    # Check for Ollama FAISS index
    if os.path.exists("faiss_index_ollama"):
        print("Migrating Ollama embeddings...")
        try:
            embedding_model = OllamaEmbeddings(model="nomic-embed-text")
            
            # Load FAISS index
            vectordb = FAISS.load_local(
                "faiss_index_ollama",
                embeddings=embedding_model,
                allow_dangerous_deserialization=True
            )
            
            # Get all documents
            docs = vectordb.similarity_search("", k=10000)  # Get all docs
            
            # Store in Qdrant
            store_documents(docs, embedding_model, collection_name="freightify_docs_ollama")
            print("✅ Successfully migrated Ollama embeddings to Qdrant")
        except Exception as e:
            print(f"❌ Error migrating Ollama embeddings: {str(e)}")
    
    print("Migration complete!")

if __name__ == "__main__":
    migrate_faiss_to_qdrant()