import os
import sys
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredExcelLoader, CSVLoader
)
import requests
import google.generativeai as genai

# Add project root to path
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Try to import Qdrant, fall back to FAISS if not available
try:
    from src.doc_analysis.tools.qdrant_store import store_documents, get_retriever
    VECTOR_DB = "qdrant"
except ImportError:
    from langchain_community.vectorstores import FAISS
    VECTOR_DB = "faiss"
    st.warning("⚠️ Qdrant not available, falling back to FAISS vector store")

def get_gemini_api_key():
    return os.getenv("GEMINI_API_KEY")

def is_cloud():
    """Check if the app is running on Streamlit Cloud or other cloud environment"""
    # Check for Streamlit Cloud environment variables
    if os.environ.get("STREAMLIT_CLOUD", "0") == "1" or "streamlit" in os.environ.get("HOME", ""):
        return True
    
    # Check for other common cloud environment variables
    if os.environ.get("DYNO") or os.environ.get("RAILWAY_STATIC_URL") or os.environ.get("VERCEL"):
        return True
    
    # Check if Ollama is available (to detect if we're in a local environment)
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=1)
        return False  # Ollama is available, so we're not in cloud
    except:
        # If we can't connect to Ollama, assume we're in cloud
        return True

# --- Load environment variables ---
load_dotenv()

# --- Check for Qdrant configuration if using Qdrant ---
if VECTOR_DB == "qdrant":
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_path = os.getenv("QDRANT_PATH")
    
    if not (qdrant_api_key and qdrant_url) and not qdrant_path:
        st.warning("⚠️ Qdrant configuration missing. Please set QDRANT_API_KEY and QDRANT_URL for cloud deployment, or QDRANT_PATH for local deployment in your .env file.")
        st.info("Using temporary in-memory storage for this session. Your data will not persist after closing the app.")

# --- UI Setup ---
st.set_page_config(page_title="Freightify Bot", layout="wide")

# Main header with logo on right
header_col1, header_col2 = st.columns([5, 1])
with header_col1:
    st.title("🚢 Freightify Bot")
with header_col2:
    logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        st.image(logo, caption=None, width=150)
    else:
        st.write("🚢")  # Fallback emoji if logo not found

# --- Sidebar Model Selectors ---
st.sidebar.title("🔧 Configuration")
st.sidebar.subheader("Choose Model for Embedding")
embedding_model_source = st.sidebar.selectbox("Embedding Model", ["Ollama", "OpenAI"] if not is_cloud() else ["OpenAI"], label_visibility="collapsed")
st.sidebar.subheader("Choose Model for Retrieval/Chat")
retrieval_model_source = st.sidebar.selectbox("Retrieval Model", ["Ollama", "OpenAI", "Gemini"] if not is_cloud() else ["OpenAI", "Gemini"], label_visibility="collapsed")

# --- Embedding Model Selection ---
# Check if we're in cloud environment or user selected OpenAI/Gemini
cloud_environment = is_cloud()
if cloud_environment:
    # Force OpenAI in cloud environments
    embedding_model_source = "OpenAI"
    st.sidebar.info("⚠️ Running in cloud environment. Using OpenAI embeddings only.")

if cloud_environment or embedding_model_source == "OpenAI" or retrieval_model_source == "Gemini":
    try:
        from langchain_openai import OpenAIEmbeddings
        embedding_model = OpenAIEmbeddings()
        embedding_label = "OpenAI"
        collection_name = "freightify_docs_openai"
        faiss_index_path = "faiss_index_openai"
    except Exception as e:
        st.error(f"Error initializing OpenAI embeddings: {str(e)}. Please check your OPENAI_API_KEY.")
        st.stop()
else:
    try:
        from langchain_community.embeddings import OllamaEmbeddings
        embedding_model = OllamaEmbeddings(model="nomic-embed-text")
        embedding_label = "Ollama"
        collection_name = "freightify_docs_ollama"
        faiss_index_path = "faiss_index_ollama"
    except Exception as e:
        st.error(f"Error initializing Ollama embeddings: {str(e)}. Falling back to OpenAI.")
        try:
            from langchain_openai import OpenAIEmbeddings
            embedding_model = OpenAIEmbeddings()
            embedding_label = "OpenAI"
            collection_name = "freightify_docs_openai"
            faiss_index_path = "faiss_index_openai"
        except Exception as e2:
            st.error(f"Error initializing OpenAI embeddings: {str(e2)}. Please check your OPENAI_API_KEY.")
            st.stop()

# --- LLM Selection ---
if retrieval_model_source == "Ollama" and not cloud_environment:
    try:
        from langchain_community.llms import Ollama
        llm = Ollama(model=st.sidebar.selectbox("Ollama Model", ["llama3", "mistral", "phi3"]))
    except Exception as e:
        st.error(f"Error initializing Ollama LLM: {str(e)}. Falling back to OpenAI.")
        retrieval_model_source = "OpenAI"
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-3.5-turbo")
        except Exception as e2:
            st.error(f"Error initializing OpenAI LLM: {str(e2)}. Please check your OPENAI_API_KEY.")
            st.stop()
elif retrieval_model_source == "OpenAI":
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(model=st.sidebar.selectbox("OpenAI Model", ["gpt-4", "gpt-3.5-turbo"]))
    except Exception as e:
        st.error(f"Error initializing OpenAI LLM: {str(e)}. Please check your OPENAI_API_KEY.")
        st.stop()
else:  # Gemini
    llm = None  # Use Gemini HTTP API as below
    # Check if GEMINI_API_KEY is set
    if not os.environ.get("GEMINI_API_KEY"):
        st.error("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")
        st.info("Continuing, but Gemini responses will fail.")


# --- File Upload (moved to right side) ---
upload_col1, upload_col2 = st.columns([3, 1])
with upload_col1:
    st.subheader(f"Upload a document to analyse with {embedding_label}:")
with upload_col2:
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt", "md", "csv", "xlsx"], label_visibility="collapsed")
if uploaded_file:
    unique_name = f"{uuid.uuid4()}_{uploaded_file.name}"
    temp_path = os.path.join("uploads", unique_name)
    os.makedirs("uploads", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext == "pdf":
        loader = PyPDFLoader(temp_path)
    elif ext in ["docx", "docs"]:
        loader = UnstructuredWordDocumentLoader(temp_path)
    elif ext == "csv":
        loader = CSVLoader(temp_path)
    elif ext == "xlsx":
        loader = UnstructuredExcelLoader(temp_path)
    else:
        loader = TextLoader(temp_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    # Add to vector store
    try:
        # In cloud environment, always use FAISS
        if cloud_environment:
            VECTOR_DB = "faiss"
        
        if VECTOR_DB == "qdrant" and not cloud_environment:
            try:
                vectordb = store_documents(chunks, embedding_model, collection_name=collection_name)
                st.success(f"Document uploaded and indexed with {embedding_label} embeddings in Qdrant! You can now ask questions about it.")
            except Exception as e:
                st.error(f"Error storing documents in Qdrant: {str(e)}")
                st.info("Falling back to FAISS vector store.")
                # Fall back to FAISS
                VECTOR_DB = "faiss"
        
        # FAISS fallback or primary option
        if VECTOR_DB == "faiss":
            # Create directory if it doesn't exist
            os.makedirs(faiss_index_path, exist_ok=True)
            
            try:
                if os.path.exists(os.path.join(faiss_index_path, "index.faiss")):
                    vectordb = FAISS.load_local(
                        faiss_index_path,
                        embeddings=embedding_model,
                        allow_dangerous_deserialization=True
                    )
                    vectordb.add_documents(chunks)
                else:
                    vectordb = FAISS.from_documents(chunks, embedding_model)
                vectordb.save_local(faiss_index_path)
                st.success(f"Document uploaded and indexed with {embedding_label} embeddings in FAISS! You can now ask questions about it.")
            except Exception as e:
                st.error(f"Error storing documents in FAISS: {str(e)}")
    except Exception as e:
        st.error(f"Error processing document: {str(e)}")

# --- Retrieval Embedding Selection ---
if retrieval_model_source == "Gemini":
    try:
        from langchain_openai import OpenAIEmbeddings
        retrieval_embedding = OpenAIEmbeddings()
        retrieval_collection_name = "freightify_docs_openai"
        retrieval_faiss_index_path = "faiss_index_openai"
    except Exception as e:
        st.error(f"Error initializing OpenAI embeddings for retrieval: {str(e)}. Please check your OPENAI_API_KEY.")
        st.stop()
else:
    retrieval_embedding = embedding_model
    retrieval_collection_name = collection_name
    retrieval_faiss_index_path = faiss_index_path

# --- Get retriever ---
try:
    # In cloud environment, always use FAISS for simplicity
    if cloud_environment:
        VECTOR_DB = "faiss"
        st.sidebar.info("⚠️ Running in cloud environment. Using FAISS vector store.")
    
    if VECTOR_DB == "qdrant":
        try:
            # Import directly from langchain to ensure compatibility
            from langchain_community.vectorstores import Qdrant
            from src.doc_analysis.tools.qdrant_store import get_qdrant_client
            
            # Get Qdrant client
            client = get_qdrant_client()
            
            # Create vector store directly to ensure correct parameters
            try:
                vector_store = Qdrant(
                    client=client,
                    collection_name=retrieval_collection_name,
                    embedding=retrieval_embedding  # Try with embedding (singular)
                )
            except Exception:
                vector_store = Qdrant(
                    client=client,
                    collection_name=retrieval_collection_name,
                    embeddings=retrieval_embedding  # Try with embeddings (plural)
                )
            
            # Create retriever
            retriever = vector_store.as_retriever(search_kwargs={"k": 4})
            
            # Test retriever
            try:
                retriever.get_relevant_documents("test")
                st.sidebar.success("✅ Connected to Qdrant successfully")
            except Exception as inner_e:
                st.sidebar.error(f"Error testing retriever: {str(inner_e)}")
                st.sidebar.info("Falling back to FAISS vector store.")
                VECTOR_DB = "faiss"  # Fall back to FAISS
        except Exception as e:
            st.sidebar.error(f"Could not connect to Qdrant: {str(e)}")
            st.sidebar.info("Falling back to FAISS vector store.")
            VECTOR_DB = "faiss"  # Fall back to FAISS
    
    # FAISS fallback or primary option
    if VECTOR_DB == "faiss":
        # Create directories if they don't exist
        os.makedirs(retrieval_faiss_index_path, exist_ok=True)
        
        if os.path.exists(os.path.join(retrieval_faiss_index_path, "index.faiss")):
            try:
                vectordb = FAISS.load_local(
                    retrieval_faiss_index_path,
                    embeddings=retrieval_embedding,
                    allow_dangerous_deserialization=True
                )
                retriever = vectordb.as_retriever(search_kwargs={"k": 4})
                st.sidebar.success("✅ Connected to FAISS successfully")
            except Exception as e:
                st.sidebar.error(f"Error loading FAISS index: {str(e)}")
                retriever = None
        else:
            st.sidebar.warning("No vector store found. Please upload documents first.")
            retriever = None
        
except Exception as e:
    st.sidebar.error(f"Could not connect to any vector store: {str(e)}")
    retriever = None

# --- Prompt Template ---
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

template = """
You are Freightify Bot, an intelligent assistant for logistics and freight teams. 
Answer questions truthfully using ONLY the context below.

Context:
{context}

Question:
{question}

Helpful Answer:
"""
prompt = PromptTemplate(input_variables=["context", "question"], template=template)

if retriever is not None and not is_cloud() and retrieval_model_source != "Gemini":
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )
else:
    qa_chain = None

# --- Agentic AI Section ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 Agentic AI")

# Import agentic components
try:
    # Project root is already in sys.path
    from src.doc_analysis.coordinator import AgentCoordinator
    from src.doc_analysis.learning_system import AdaptiveLearning
    
    st.sidebar.subheader("Agent Mode")
    agentic_mode = st.sidebar.selectbox(
        "Select Agent Mode",
        ["Standard Chat", "Multi-Agent Analysis", "Learning Enhanced"],
        label_visibility="collapsed"
    )
except ImportError:
    agentic_mode = "Standard Chat"
    st.sidebar.warning("⚠️ Agentic features not available")

# --- Chat UI ---
st.markdown("---")
st.subheader("💬 Chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Create a container for chat messages with fixed height
chat_container = st.container()
chat_container.markdown("<div style='min-height: 400px;'></div>", unsafe_allow_html=True)

with chat_container:
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Chat input
query = st.chat_input("Type your question here...")


if query and retriever:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message in chat
    with st.chat_message("user"):
        st.write(query)
    
    # Agentic AI Enhancement
    if 'agentic_mode' in locals() and agentic_mode == "Multi-Agent Analysis":
        with st.chat_message("assistant"):
            with st.spinner("🤖 Multi-Agent Analysis..."):
                try:
                    # Use the current retriever's documents for agentic analysis
                    docs = retriever.get_relevant_documents(query)
                    context = "\n\n".join([doc.page_content for doc in docs])
                    
                    # Create enhanced prompt for multi-agent analysis
                    enhanced_prompt = f"""Based on this context from uploaded documents:
{context}

Query: {query}

Provide a comprehensive multi-perspective analysis including:
1. Summary of key points
2. Detailed test scenarios
3. Process workflows
4. Edge cases and considerations"""
                    
                    coordinator = AgentCoordinator()
                    
                    # Determine the appropriate analysis mode based on the query
                    if any(keyword in query.lower() for keyword in ["summarize", "summary", "overview", "explain", "what is", "how does", "knowledge"]):
                        analysis_mode = "summary"
                    elif any(keyword in query.lower() for keyword in ["test", "scenario", "case", "validation"]):
                        analysis_mode = "testing"
                    else:
                        analysis_mode = "balanced"
                    
                    result_text = coordinator.collaborative_analysis(enhanced_prompt, mode=analysis_mode)
                    st.markdown("🤖 **Multi-Agent Analysis:**")
                    st.write(result_text)
                    
                    # Show source documents
                    with st.expander("📄 Source Documents Used"):
                        for doc in docs:
                            st.markdown(f"**{os.path.basename(doc.metadata.get('source', ''))}**")
                            st.write(doc.page_content[:300] + "...")
                    
                    # Add to chat history
                    st.session_state.messages.append({"role": "assistant", "content": f"🤖 **Multi-Agent Analysis:**\n\n{result_text}"})
                        
                except Exception as e:
                    st.error(f"Agentic analysis failed: {str(e)}")
                    # Fallback to standard mode
                    agentic_mode = "Standard Chat"
    
    elif 'agentic_mode' in locals() and agentic_mode == "Learning Enhanced":
        with st.chat_message("assistant"):
            with st.spinner("🧠 Learning Enhanced Analysis..."):
                try:
                    learning = AdaptiveLearning()
                    enhanced_query = learning.get_query_suggestions(query)
                    st.info(f"📝 Enhanced query: {enhanced_query}")
                    query = enhanced_query  # Use enhanced query
                    
                    # Continue with enhanced query processing
                    if retrieval_model_source == "Gemini":
                        docs = retriever.get_relevant_documents(query)
                        context = "\n\n".join([doc.page_content for doc in docs])
                        gemini_prompt = f"""
You are Freightify Bot, an intelligent assistant for logistics and freight teams. 
Answer questions truthfully using ONLY the context below.

Context:
{context}

Question:
{query}

Helpful Answer:
"""
                        api_key = os.environ["GEMINI_API_KEY"]
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
                        data = {
                            "contents": [{"parts": [{"text": gemini_prompt}]}]
                        }
                        response = requests.post(url, json=data)
                        result = response.json()
                        if "candidates" in result:
                            answer = result["candidates"][0]["content"]["parts"][0]["text"]
                        else:
                            answer = result.get("error", {}).get("message", "Unknown error from Gemini API")
                        
                        st.write(answer)
                        with st.expander("🗂 Source Documents"):
                            for doc in docs:
                                st.markdown(f"**📄 {os.path.basename(doc.metadata.get('source', ''))}**")
                                st.write(doc.page_content[:300] + "...")
                        
                        # Add to chat history
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    elif qa_chain is not None:
                        result = qa_chain.invoke({"query": query})
                        st.write(result["result"])
                        with st.expander("🗂 Source Documents"):
                            for doc in result["source_documents"]:
                                st.markdown(f"**📄 {os.path.basename(doc.metadata.get('source', ''))}**")
                                st.write(doc.page_content[:300] + "...")
                        
                        # Add to chat history
                        st.session_state.messages.append({"role": "assistant", "content": result["result"]})
                    
                    else:
                        message = "No vectorstore found. Please upload documents first."
                        st.warning(message)
                        st.session_state.messages.append({"role": "assistant", "content": message})
                        
                except Exception as e:
                    error_msg = f"Learning enhancement failed: {str(e)}"
                    st.warning(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Standard or fallback processing
    elif 'agentic_mode' not in locals() or agentic_mode == "Standard Chat":
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                if retrieval_model_source == "Gemini":
                    docs = retriever.get_relevant_documents(query)
                    context = "\n\n".join([doc.page_content for doc in docs])
                    gemini_prompt = f"""
You are Freightify Bot, an intelligent assistant for logistics and freight teams. 
Answer questions truthfully using ONLY the context below.

Context:
{context}

Question:
{query}

Helpful Answer:
"""
                    api_key = os.environ["GEMINI_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
                    data = {
                        "contents": [{"parts": [{"text": gemini_prompt}]}]
                    }
                    response = requests.post(url, json=data)
                    result = response.json()
                    if "candidates" in result:
                        answer = result["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        answer = result.get("error", {}).get("message", "Unknown error from Gemini API")
                    
                    st.write(answer)
                    with st.expander("🗂 Source Documents"):
                        for doc in docs:
                            st.markdown(f"**📄 {os.path.basename(doc.metadata.get('source', ''))}**")
                            st.write(doc.page_content[:300] + "...")
                    
                    # Add to chat history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                
                elif qa_chain is not None:
                    result = qa_chain.invoke({"query": query})
                    st.write(result["result"])
                    with st.expander("🗂 Source Documents"):
                        for doc in result["source_documents"]:
                            st.markdown(f"**📄 {os.path.basename(doc.metadata.get('source', ''))}**")
                            st.write(doc.page_content[:300] + "...")
                    
                    # Add to chat history
                    st.session_state.messages.append({"role": "assistant", "content": result["result"]})
                
                else:
                    message = "No vectorstore found. Please upload documents first."
                    st.warning(message)
                    st.session_state.messages.append({"role": "assistant", "content": message})

            # --- Feedback with better alignment ---
        feedback_cols = st.columns([1, 1, 3])
        with feedback_cols[0]:
            thumbs_up = st.button("👍 Helpful", key=f"thumbs_up_{query}", use_container_width=True)
        with feedback_cols[1]:
            thumbs_down = st.button("👎 Not Helpful", key=f"thumbs_down_{query}", use_container_width=True)
        feedback_given = thumbs_up or thumbs_down
        feedback_comment = None
        if feedback_given:
            feedback_type = "thumbs_up" if thumbs_up else "thumbs_down"
            feedback_comment = st.text_area(
                "Optional: Please provide additional feedback to help us improve.",
                key=f"feedback_comment_{feedback_type}_{query}"
            )
            if st.button("Submit Feedback", key=f"submit_feedback_{feedback_type}_{query}"):
                import json
                feedback_data = {
                    "query": query,
                    "response": result["result"] if retrieval_model_source != "Gemini" else answer,
                    "sources": [doc.metadata.get('source', '') for doc in result["source_documents"]] if retrieval_model_source != "Gemini" else [doc.metadata.get('source', '') for doc in docs],
                    "feedback": feedback_type,
                    "comment": feedback_comment or "",
                    "retrieval_model": retrieval_model_source,
                    "embedding_model": embedding_model_source
                }
                with open("feedback_log.jsonl", "a") as f:
                    f.write(json.dumps(feedback_data) + "\n")
                st.success("✅ Feedback recorded! Thank you for your input.")

# --- Integrations Section ---
st.sidebar.markdown("---")
st.sidebar.subheader("🔗 Integrations")

# Jira Integration
with st.sidebar.expander("Jira Integration"):
    jira_url = st.text_input("Jira Base URL (e.g. https://yourcompany.atlassian.net)")
    jira_email = st.text_input("Jira Email")
    jira_token = st.text_input("Jira API Token", type="password")
    jira_ticket = st.text_input("Jira Ticket Number")
    jira_fetch = st.button("Fetch Jira Issues", use_container_width=True)

# Freshworks Integration
with st.sidebar.expander("Freshworks Integration"):
    freshworks_domain = st.text_input("Freshworks Domain (e.g. yourcompany.freshdesk.com)")
    freshworks_api_key = st.text_input("Freshworks API Key", type="password")
    ticket_id = st.text_input("Ticket ID (optional)")
    freshworks_fetch = st.button("Fetch Freshworks Tickets", use_container_width=True)
    
# Google Drive Integration
with st.sidebar.expander("Google Drive Integration"):
    st.markdown("🔍 **Access Google Drive Documents**")
    
    # Authentication options
    auth_method = st.radio(
        "Authentication Method",
        ["API Key", "OAuth"],
        horizontal=True
    )
    
    if auth_method == "API Key":
        google_api_key = st.text_input("Google API Key", type="password")
    else:
        st.info("🔒 OAuth requires additional setup. Click 'Authenticate' to begin the process.")
        st.button("Authenticate with Google")
    
    # Document selection
    doc_option = st.radio(
        "Document Selection",
        ["Document ID", "Folder ID", "Recent Documents"],
        horizontal=True
    )
    
    if doc_option == "Document ID":
        doc_id = st.text_input("Google Document ID")
    elif doc_option == "Folder ID":
        folder_id = st.text_input("Google Drive Folder ID")
        max_docs = st.slider("Maximum Documents", 1, 20, 5)
    
    google_fetch = st.button("📥 Fetch Google Documents", use_container_width=True)


def fetch_jira_issues(jira_url, email, api_token, jql="ORDER BY created DESC", max_results=10):
    headers = {"Accept": "application/json"}
    auth = (email, api_token)
    params = {"jql": jql, "maxResults": max_results}
    response = requests.get(f"{jira_url}/rest/api/2/search", headers=headers, params=params, auth=auth)
    response.raise_for_status()
    data = response.json()
    docs = []
    for issue in data["issues"]:
        key = issue["key"]
        summary = issue["fields"]["summary"]
        description = issue["fields"].get("description", "")
        content = f"Jira Issue {key}\nSummary: {summary}\nDescription: {description}"
        docs.append({"content": content, "metadata": {"source": f"jira:{key}"}})
    return docs

# For a single issue:
def fetch_single_jira_issue(jira_url, email, api_token, issue_key):
    headers = {"Accept": "application/json"}
    auth = (email, api_token)
    # Only add the path, not the full URL
    url = f"{jira_url}/rest/api/2/issue/{issue_key}"
    response = requests.get(url, headers=headers, auth=auth)
    response.raise_for_status()
    issue = response.json()
    key = issue["key"]
    summary = issue["fields"]["summary"]
    description = issue["fields"].get("description", "")
    content = f"Jira Issue {key}\nSummary: {summary}\nDescription: {description}"
    return [{"content": content, "metadata": {"source": f"jira:{key}"}}]
    
# Process Jira fetch request
if jira_fetch and jira_url and jira_email and jira_token:
    with st.spinner("Fetching Jira issues..."):
        try:
            if jira_ticket:
                # Fetch a single issue
                jira_docs = fetch_single_jira_issue(jira_url, jira_email, jira_token, jira_ticket)
            else:
                # Fetch multiple issues as before
                jira_docs = fetch_jira_issues(jira_url, jira_email, jira_token)
            # Convert to LangChain Document objects
            from langchain.schema import Document
            docs = [Document(page_content=d["content"], metadata=d["metadata"]) for d in jira_docs]
            splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
            chunks = splitter.split_documents(docs)
            upload_vectordb = FAISS.from_documents(chunks, embedding_model)
            upload_vectordb.save_local(faiss_index_path)
            if chunks:
                success_msg = f"Fetched and indexed {len(jira_docs)} Jira issues!"
                st.success(success_msg)
                # Add system message to chat
                st.session_state.messages.append({"role": "assistant", "content": f"📄 {success_msg}"})  
            else:
                st.warning("No content to index from Jira issues (issues may be empty or too short).")
        except Exception as e:
            st.error(f"Failed to fetch Jira issues: {e}")

# Process Freshworks fetch request
if freshworks_fetch and freshworks_domain and freshworks_api_key:
    with st.spinner("Fetching Freshworks tickets..."):
        try:
            # Import the Freshworks fetcher
            # Project root is already in sys.path
            from src.doc_analysis.tools.freshworks_fetcher import fetch_and_embed_freshworks_ticket
            
            # Fetch tickets
            if ticket_id:
                result = fetch_and_embed_freshworks_ticket(ticket_id, freshworks_domain, freshworks_api_key)
                success_msg = f"Fetched and indexed Freshworks ticket {ticket_id}"
            else:
                result = fetch_and_embed_freshworks_ticket(None, freshworks_domain, freshworks_api_key)
                success_msg = "Fetched and indexed recent Freshworks tickets"
            
            if "✅" in result:
                st.success(success_msg)
                # Add system message to chat
                st.session_state.messages.append({"role": "assistant", "content": f"📄 {success_msg}"})  
            else:
                st.warning(result)
        except Exception as e:
            st.error(f"Failed to fetch Freshworks tickets: {e}")

# Process Google Drive fetch request
if google_fetch:
    with st.spinner("Fetching Google Drive documents..."):
        try:
            # Import the Google Drive fetcher
            # Project root is already in sys.path
            from src.doc_analysis.tools.google_drive_fetcher import fetch_google_drive_documents
            
            # Determine which fetch method to use
            if auth_method == "API Key" and google_api_key:
                if doc_option == "Document ID" and 'doc_id' in locals() and doc_id:
                    result = fetch_google_drive_documents(doc_id=doc_id, api_key=google_api_key)
                    success_msg = f"Fetched and indexed Google document"
                elif doc_option == "Folder ID" and 'folder_id' in locals() and folder_id:
                    result = fetch_google_drive_documents(folder_id=folder_id, max_docs=max_docs, api_key=google_api_key)
                    success_msg = f"Fetched and indexed documents from Google Drive folder"
                else:
                    result = fetch_google_drive_documents(max_docs=5, api_key=google_api_key)
                    success_msg = "Fetched and indexed recent Google Drive documents"
                
                if "✅" in result:
                    st.success(success_msg)
                    # Add system message to chat
                    st.session_state.messages.append({"role": "assistant", "content": f"📄 {success_msg}"})
                else:
                    st.warning(result)
            else:
                st.warning("Please provide a Google API key and select document options")
        except Exception as e:
            st.error(f"Failed to fetch Google Drive documents: {e}")