import sys
import os
sys.modules["sqlite3"] = __import__("pysqlite3")
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader, UnstructuredExcelLoader, CSVLoader
)
import requests

# --- Gemini imports ---
import google.generativeai as genai

def get_gemini_api_key():
    return os.getenv("GEMINI_API_KEY")

# --- Load environment variables ---
load_dotenv()

# --- UI Setup ---
st.set_page_config(page_title="Freightify Bot", layout="wide")
col1, col2 = st.columns([4, 1])
with col2:
    logo = Image.open("scripts/logo.jpg")
    st.image(logo, caption=None, use_container_width=True)
with col1:
    st.title("🚢 Freightify Bot")

# --- Sidebar Model Selectors ---
st.sidebar.title("🔧 Configuration")
embedding_model_source = st.sidebar.selectbox("Choose Model for Embedding", ["Ollama", "OpenAI"])
retrieval_model_source = st.sidebar.selectbox("Choose Model for Retrieval/Chat", ["Ollama", "OpenAI", "Gemini"])

# --- Embedding Model and Vectorstore for Upload ---
if embedding_model_source == "Ollama":
    from langchain_community.embeddings import OllamaEmbeddings
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")
    embedding_chroma_path = "vectorstore_ollama"
    embedding_label = "Ollama"
else:
    from langchain_openai import OpenAIEmbeddings
    embedding_model = OpenAIEmbeddings()
    embedding_chroma_path = "vectorstore_openai"
    embedding_label = "OpenAI"

# --- Retrieval Model and Vectorstore for Chat ---
if retrieval_model_source == "Ollama":
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_community.llms import Ollama
    retrieval_embedding = OllamaEmbeddings(model="nomic-embed-text")
    llm = Ollama(model=st.sidebar.selectbox("Ollama Model", ["llama3", "mistral", "phi3"]))
    retrieval_chroma_path = "vectorstore_ollama"
    use_gemini = False
elif retrieval_model_source == "OpenAI":
    from langchain_openai import OpenAIEmbeddings, ChatOpenAI
    retrieval_embedding = OpenAIEmbeddings()
    llm = ChatOpenAI(model=st.sidebar.selectbox("OpenAI Model", ["gpt-4", "gpt-3.5-turbo"]))
    retrieval_chroma_path = "vectorstore_openai"
    use_gemini = False
else:  # Gemini
    retrieval_embedding = None  # Not used for Gemini LLM
    llm = None  # Not used for Gemini LLM
    retrieval_chroma_path = "vectorstore_openai"  # Use OpenAI embeddings for RAG
    use_gemini = True
    gemini_api_key = get_gemini_api_key()
    if not gemini_api_key:
        st.error("GEMINI_API_KEY not set in Streamlit secrets or environment.")
    else:
        os.environ["GEMINI_API_KEY"] = gemini_api_key
        # This line was causing the error, so it's commented out.
        # model = genai.GenerativeModel('gemini-pro') 

# When Gemini is selected for chat, still use OpenAI or Ollama for embeddings
if retrieval_model_source == "Gemini":
    # Use the same embedding function as for file upload
    if embedding_model_source == "Ollama":
        from langchain_community.embeddings import OllamaEmbeddings
        retrieval_embedding = OllamaEmbeddings(model="nomic-embed-text")
        retrieval_chroma_path = "vectorstore_ollama"
    else:
        from langchain_openai import OpenAIEmbeddings
        retrieval_embedding = OpenAIEmbeddings()
        retrieval_chroma_path = "vectorstore_openai"
    # Set up Chroma with the correct embedding function
    vectordb = Chroma(persist_directory=retrieval_chroma_path, embedding_function=retrieval_embedding)
    retriever = vectordb.as_retriever()
    # ... then use Gemini for the LLM as you do now

vectordb = Chroma(persist_directory=retrieval_chroma_path, embedding_function=retrieval_embedding)
retriever = vectordb.as_retriever()

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

if not use_gemini:
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt},
    )

# --- File Upload ---
st.subheader(f"Upload a document to index with {embedding_label} embeddings:")
uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt", "md", "csv", "xlsx"])
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
    # Add to the selected embedding model's vectorstore
    upload_vectordb = Chroma(persist_directory=embedding_chroma_path, embedding_function=embedding_model)
    upload_vectordb.add_documents(chunks)
    st.success(f"Document uploaded and indexed with {embedding_label} embeddings! You can now ask questions about it.")

# --- Chat UI ---
st.subheader("💬 Ask your question")
query = st.text_input("Type your question here:")

if query:
    with st.spinner("🤔 Thinking..."):
        if not use_gemini:
            result = qa_chain.invoke({"query": query})
            st.markdown("### 📌 Answer:")
            st.write(result["result"])
            with st.expander("🗂 Source Documents"):
                for doc in result["source_documents"]:
                    st.markdown(f"**📄 {os.path.basename(doc.metadata.get('source', ''))}**")
                    st.write(doc.page_content[:500] + "...")
        else:
            # Gemini RAG: retrieve context, then call Gemini
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
            st.markdown("### 📌 Answer:")
            st.write(answer)
            with st.expander("🗂 Source Documents"):
                for doc in docs:
                    st.markdown(f"**📄 {os.path.basename(doc.metadata.get('source', ''))}**")
                    st.write(doc.page_content[:500] + "...")

        # --- Feedback ---
        feedback_col1, feedback_col2 = st.columns([1, 1])
        with feedback_col1:
            thumbs_up = st.button("👍 Helpful", key=f"thumbs_up_{query}")
        with feedback_col2:
            thumbs_down = st.button("👎 Not Helpful", key=f"thumbs_down_{query}")
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
                    "response": result["result"] if not use_gemini else answer,
                    "sources": [doc.metadata.get('source', '') for doc in result["source_documents"]] if not use_gemini else [doc.metadata.get('source', '') for doc in docs],
                    "feedback": feedback_type,
                    "comment": feedback_comment or "",
                    "retrieval_model": retrieval_model_source,
                    "embedding_model": embedding_model_source
                }
                with open("feedback_log.jsonl", "a") as f:
                    f.write(json.dumps(feedback_data) + "\n")
                st.success("✅ Feedback recorded! Thank you for your input.")

st.sidebar.markdown("### Jira Integration")
jira_url = st.sidebar.text_input("Jira Base URL (e.g. https://yourcompany.atlassian.net)")
jira_email = st.sidebar.text_input("Jira Email")
jira_token = st.sidebar.text_input("Jira API Token", type="password")
jira_ticket = st.sidebar.text_input("Jira Ticket Number")
jira_fetch = st.sidebar.button("Fetch Jira Issues")


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
    
if jira_fetch and jira_url and jira_email and jira_token:
    with st.spinner("Fetching Jira issues..."):
        try:
            if jira_ticket:
                # Fetch a single issue
                issue_url = f"{jira_url}/rest/api/2/issue/{jira_ticket}"
                response = requests.get(issue_url, auth=(jira_email, jira_token), headers={"Accept": "application/json"})
                response.raise_for_status()
                issue = response.json()
                key = issue["key"]
                summary = issue["fields"]["summary"]
                description = issue["fields"].get("description", "")
                content = f"Jira Issue {key}\nSummary: {summary}\nDescription: {description}"
                jira_docs = [{"content": content, "metadata": {"source": f"jira:{key}"}}]
            else:
                # Fetch multiple issues as before
                jira_docs = fetch_jira_issues(jira_url, jira_email, jira_token)
            # Convert to LangChain Document objects
            from langchain.schema import Document
            docs = [Document(page_content=d["content"], metadata=d["metadata"]) for d in jira_docs]
            splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
            chunks = splitter.split_documents(docs)
            upload_vectordb = Chroma(persist_directory=embedding_chroma_path, embedding_function=embedding_model)
            if chunks:
                upload_vectordb.add_documents(chunks)
                st.success(f"Fetched and indexed {len(jira_docs)} Jira issues!")
            else:
                st.warning("No content to index from Jira issues (issues may be empty or too short).")
        except Exception as e:
            st.error(f"Failed to fetch Jira issues: {e}")


