import os
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_qdrant_client():
    """Get Qdrant client using environment variables"""
    # Check for cloud deployment first
    api_key = os.getenv("QDRANT_API_KEY")
    url = os.getenv("QDRANT_URL")
    
    if api_key and url:
        # Cloud deployment
        return QdrantClient(url=url, api_key=api_key)
    else:
        # Local deployment
        path = os.getenv("QDRANT_PATH", "./qdrant_data")
        return QdrantClient(path=path)

def get_or_create_collection(collection_name="freightify_docs", dimension=1536):
    """Get existing collection or create if it doesn't exist"""
    client = get_qdrant_client()
    
    # Check if collection exists
    collections = client.get_collections().collections
    collection_names = [collection.name for collection in collections]
    
    if collection_name not in collection_names:
        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=dimension,
                distance=models.Distance.COSINE
            )
        )
    
    return client

def store_documents(documents, embedding_model, collection_name="freightify_docs", batch_size=100):
    """Store documents in Qdrant"""
    # Determine embedding dimension
    if isinstance(embedding_model, OpenAIEmbeddings):
        dimension = 1536
    else:
        # For other embedding models, default to 768
        dimension = 768
    
    # Initialize Qdrant and get/create collection
    client = get_or_create_collection(collection_name, dimension)
    
    # Create vector store
    vector_store = Qdrant.from_documents(
        documents=documents,
        embedding=embedding_model,  # This is correct for from_documents
        collection_name=collection_name,
        client=client,
        batch_size=batch_size
    )
    
    return vector_store

def get_retriever(embedding_model, collection_name="freightify_docs", k=4):
    """Get a retriever for the Qdrant collection"""
    # Initialize Qdrant client
    client = get_qdrant_client()
    
    # Create vector store - use the correct parameter name based on LangChain version
    try:
        # First try with 'embedding' (singular)
        vector_store = Qdrant(
            client=client,
            collection_name=collection_name,
            embedding=embedding_model
        )
    except Exception:
        try:
            # Then try with 'embeddings' (plural)
            vector_store = Qdrant(
                client=client,
                collection_name=collection_name,
                embeddings=embedding_model
            )
        except Exception:
            # Last resort - try with embedding_function
            vector_store = Qdrant(
                client=client,
                collection_name=collection_name,
                embedding_function=embedding_model
            )
    
    # Return retriever
    return vector_store.as_retriever(search_kwargs={"k": k})