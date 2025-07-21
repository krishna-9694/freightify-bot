from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from crewai.tools import tool
import os

@tool("Context Retriever Tool")
def retrieve_context_from_docs(query: str) -> str:
    """Embeds a query and retrieves relevant chunks from vector DB"""
    try:
        # Use vectorstore_openai since we have OpenAI embeddings (1536 dim)
        vectorstore_path = "vectorstore_openai"
        
        vectordb = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=OpenAIEmbeddings()
        )
        results = vectordb.similarity_search(query, k=5)
        return "\n\n".join([r.page_content for r in results])
    except Exception as e:
        return f"Error retrieving context: {str(e)}"

