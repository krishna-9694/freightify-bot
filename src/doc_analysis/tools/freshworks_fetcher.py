import os
import requests
import json
from crewai.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

@tool("Fetch and Embed Freshworks Ticket")
def fetch_and_embed_freshworks_ticket(ticket_id: str = None, domain: str = None, api_key: str = None) -> str:
    """
    Fetches Freshworks tickets and embeds them into Chroma vector DB if not already embedded.
    Returns the embedded content or retrieved content.
    """
    # Use parameters or environment variables
    domain = domain or os.getenv("FRESHWORKS_DOMAIN")
    api_key = api_key or os.getenv("FRESHWORKS_API_KEY")

    if not domain or not api_key:
        return "❌ Missing Freshworks credentials. Please provide domain and API key."

    # Get project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    chroma_path = os.path.join(project_root, "vectorstore_openai")
    
    # Create directory if it doesn't exist
    os.makedirs(chroma_path, exist_ok=True)
    
    vectordb = Chroma(
        persist_directory=chroma_path,
        embedding_function=OpenAIEmbeddings()
    )

    # Fetch specific ticket or recent tickets
    if ticket_id:
        return _fetch_single_ticket(ticket_id, domain, api_key, vectordb)
    else:
        return _fetch_recent_tickets(domain, api_key, vectordb)

def _fetch_single_ticket(ticket_id, domain, api_key, vectordb):
    """Fetch a single ticket by ID"""
    url = f"https://{domain}/api/v2/tickets/{ticket_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        ticket = response.json()
        
        # Check if this ticket is already embedded
        existing = vectordb.similarity_search(f"Freshworks ticket {ticket_id}", k=1)
        if existing and f"Ticket: {ticket_id}" in existing[0].page_content:
            return f"✅ Retrieved from cache:\n{existing[0].page_content[:500]}"
        
        # Extract ticket data
        subject = ticket.get("subject", "")
        description = ticket.get("description", "")
        status = ticket.get("status", "")
        priority = ticket.get("priority", "")
        
        # Format content
        content = f"Ticket: {ticket_id}\nSubject: {subject}\nStatus: {status}\nPriority: {priority}\nDescription:\n{description}"
        
        # Create document and add to vector store
        doc = Document(page_content=content, metadata={"source": f"freshworks:{ticket_id}"})
        vectordb.add_documents([doc])
        vectordb.persist()
        
        return f"✅ Embedded and stored:\n{content[:500]}"
    
    except Exception as e:
        return f"❌ Failed to fetch or store Freshworks ticket: {str(e)}"

def _fetch_recent_tickets(domain, api_key, vectordb, limit=5):
    """Fetch recent tickets"""
    url = f"https://{domain}/api/v2/tickets?order_by=created_at&order_type=desc&per_page={limit}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tickets = response.json()
        
        if not tickets or "tickets" not in tickets:
            return "❌ No tickets found or invalid response format."
        
        embedded_count = 0
        for ticket in tickets["tickets"]:
            ticket_id = ticket.get("id")
            subject = ticket.get("subject", "")
            description = ticket.get("description", "")
            status = ticket.get("status", "")
            priority = ticket.get("priority", "")
            
            # Format content
            content = f"Ticket: {ticket_id}\nSubject: {subject}\nStatus: {status}\nPriority: {priority}\nDescription:\n{description}"
            
            # Create document and add to vector store
            doc = Document(page_content=content, metadata={"source": f"freshworks:{ticket_id}"})
            vectordb.add_documents([doc])
            embedded_count += 1
        
        vectordb.persist()
        return f"✅ Embedded {embedded_count} recent Freshworks tickets."
    
    except Exception as e:
        return f"❌ Failed to fetch or store Freshworks tickets: {str(e)}"