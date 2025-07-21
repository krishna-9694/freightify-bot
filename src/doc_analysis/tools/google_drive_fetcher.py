import os
import io
import json
from typing import List, Optional
from crewai.tools import tool
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

@tool("Fetch Google Drive Documents")
def fetch_google_drive_documents(
    doc_id: Optional[str] = None,
    folder_id: Optional[str] = None,
    max_docs: int = 5,
    api_key: Optional[str] = None
) -> str:
    """
    Fetches documents from Google Drive and indexes them for search.
    Provide either a specific document ID or a folder ID to fetch multiple documents.
    """
    api_key = api_key or os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return "❌ No Google API key provided. Please set GOOGLE_API_KEY in environment or provide as parameter."
    
    try:
        # Import Google API libraries
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaIoBaseDownload
        except ImportError:
            return "❌ Google API client libraries not installed. Run: pip install google-api-python-client"
        
        # Initialize the Drive API client
        drive_service = build('drive', 'v3', developerKey=api_key)
        
        if doc_id:
            # Fetch a single document
            return _fetch_single_document(drive_service, doc_id)
        elif folder_id:
            # Fetch documents from a folder
            return _fetch_folder_documents(drive_service, folder_id, max_docs)
        else:
            # Fetch recent documents
            return _fetch_recent_documents(drive_service, max_docs)
    
    except Exception as e:
        return f"❌ Error accessing Google Drive: {str(e)}"

def _fetch_single_document(drive_service, doc_id: str) -> str:
    """Fetch and process a single document by ID"""
    try:
        # Get document metadata
        file_metadata = drive_service.files().get(fileId=doc_id, fields="name,mimeType").execute()
        file_name = file_metadata.get('name', 'Unknown')
        mime_type = file_metadata.get('mimeType', '')
        
        # Download file content
        request = drive_service.files().export_media(fileId=doc_id, mimeType='text/plain') \
            if 'google-apps' in mime_type else drive_service.files().get_media(fileId=doc_id)
        
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        
        content = file_content.getvalue().decode('utf-8')
        
        # Create document and add to vector store
        doc = Document(page_content=content, metadata={"source": f"gdrive:{doc_id}", "title": file_name})
        _add_to_vector_store([doc])
        
        return f"✅ Successfully indexed Google Drive document: {file_name}"
    
    except Exception as e:
        return f"❌ Error processing document {doc_id}: {str(e)}"

def _fetch_folder_documents(drive_service, folder_id: str, max_docs: int) -> str:
    """Fetch and process documents from a folder"""
    try:
        # List files in the folder
        results = drive_service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=max_docs,
            fields="files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        if not files:
            return f"❌ No files found in folder {folder_id}"
        
        # Process each file
        processed_count = 0
        for file in files:
            try:
                result = _fetch_single_document(drive_service, file['id'])
                if "✅" in result:
                    processed_count += 1
            except Exception:
                continue
        
        return f"✅ Successfully indexed {processed_count} documents from Google Drive folder"
    
    except Exception as e:
        return f"❌ Error accessing folder {folder_id}: {str(e)}"

def _fetch_recent_documents(drive_service, max_docs: int) -> str:
    """Fetch and process recent documents"""
    try:
        # List recent files
        results = drive_service.files().list(
            pageSize=max_docs,
            orderBy="modifiedTime desc",
            fields="files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        if not files:
            return "❌ No recent files found"
        
        # Process each file
        processed_count = 0
        for file in files:
            try:
                result = _fetch_single_document(drive_service, file['id'])
                if "✅" in result:
                    processed_count += 1
            except Exception:
                continue
        
        return f"✅ Successfully indexed {processed_count} recent documents from Google Drive"
    
    except Exception as e:
        return f"❌ Error accessing recent documents: {str(e)}"

def _add_to_vector_store(docs: List[Document]) -> None:
    """Add documents to the vector store"""
    embedding_model = OpenAIEmbeddings()
    
    # Get project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    faiss_path = os.path.join(project_root, "faiss_index_openai")
    
    # Create directory if it doesn't exist
    os.makedirs(faiss_path, exist_ok=True)
    
    # Check if vector store exists
    if os.path.exists(os.path.join(faiss_path, "index.faiss")):
        vectordb = FAISS.load_local(
            faiss_path,
            embedding_model,
            allow_dangerous_deserialization=True
        )
        vectordb.add_documents(docs)
    else:
        vectordb = FAISS.from_documents(docs, embedding_model)
    
    vectordb.save_local(faiss_path)