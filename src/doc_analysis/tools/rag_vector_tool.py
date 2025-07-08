from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from crewai.tools import tool
import os
from dotenv import load_dotenv
load_dotenv()

@tool("Context Retriever Tool")
def retrieve_context_from_docs(query: str) -> str:
    """Embeds a query and retrieves relevant chunks from vector DB"""
    vectordb = Chroma(
        persist_directory="vectorstore",
        embedding_function=OpenAIEmbeddings()
    )
    results = vectordb.similarity_search(query, k=5)
    return "\n\n".join([r.page_content for r in results])

