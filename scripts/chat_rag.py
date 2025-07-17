import os
import json
import streamlit as st
from PIL import Image

from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain_chroma import Chroma
from langchain.vectorstores.base import VectorStoreRetriever
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import uuid

from collections import Counter, defaultdict

# --- Setup ---
st.set_page_config(page_title="Freightify Bot", layout="wide")

# --- Logo and Title ---
col1, col2 = st.columns([4, 1])
with col2:
    logo_path = "scripts/logo.jpg"  # Adjust as needed
    try:
        image = Image.open(logo_path)
        st.image(image, caption="Trade Simplified!", use_container_width=True)
    except Exception as e:
        st.warning("⚠️ Could not load logo image.")

with col1:
    st.title("📦 Freightify Bot")
    st.markdown("Your AI assistant for document Q&A, powered by OpenAI and ChromaDB.")

# --- Load Embeddings and Vector Store ---
CHROMA_PATH = "vectorstore_nomic"
embedding = OpenAIEmbeddings()
vectordb = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding)

retriever: VectorStoreRetriever = vectordb.as_retriever(search_kwargs={"k": 3})

# --- Custom Prompt Template ---
prompt_template = """Use the following context to answer the question.
If you don't know the answer, just say you don't know. Do not try to make up an answer.

Context:
{summaries}

Question: {question}
Answer:"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["summaries", "question"]
)

# --- LLM Setup ---
llm = ChatOpenAI(model="gpt-4", temperature=0)

qa_chain = load_qa_with_sources_chain(llm, chain_type="stuff", prompt=prompt)
qa_pipeline = RetrievalQA(combine_documents_chain=qa_chain, retriever=retriever, return_source_documents=True)

# --- UI Interaction ---
st.subheader("💬 Ask your question")
query = st.text_input("Type your question here:")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt", "md", "csv"])
if uploaded_file:
    # Save file with a unique name
    unique_name = f"{uuid.uuid4()}_{uploaded_file.name}"
    temp_path = os.path.join("uploads", unique_name)
    os.makedirs("uploads", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # Load document
    ext = uploaded_file.name.split(".")[-1].lower()
    if ext == "pdf":
        loader = PyPDFLoader(temp_path)
    elif ext in ["docx", "docs"]:
        loader = UnstructuredWordDocumentLoader(temp_path)
    elif ext == "csv":
        loader = CSVLoader(temp_path)
    else:
        loader = TextLoader(temp_path)
    docs = loader.load()
    # Split and embed
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    vectordb.add_documents(chunks)
    st.success("Document uploaded and indexed! You can now ask questions about it.")
    # Optionally, delete the file after processing
    # os.remove(temp_path) # This line is commented out to keep uploaded files

if query:
    with st.spinner("💡 Thinking..."):
        result = qa_pipeline.invoke({"query": query})
        st.markdown(f"### 🤖 Answer\n{result['result']}")

        # --- Sources ---
        with st.expander("📚 Source Documents"):
            for doc in result["source_documents"]:
                st.markdown(f"- **Source:** `{doc.metadata.get('source', 'unknown')}`")
                st.text(doc.page_content[:1000])  # Preview

        # --- Feedback ---
        feedback_col1, feedback_col2 = st.columns([1, 1])
        with feedback_col1:
            thumbs_up = st.button("👍 Helpful", key="thumbs_up")
        with feedback_col2:
            thumbs_down = st.button("👎 Not Helpful", key="thumbs_down")

        feedback_given = thumbs_up or thumbs_down
        feedback_comment = None
        if feedback_given:
            feedback_type = "thumbs_up" if thumbs_up else "thumbs_down"
            feedback_comment = st.text_area(
                "Optional: Please provide additional feedback to help us improve.",
                key=f"feedback_comment_{feedback_type}_{query}"
            )
            if st.button("Submit Feedback", key=f"submit_feedback_{feedback_type}_{query}"):
                feedback_data = {
                    "query": query,
                    "response": result['result'],
                    "sources": [doc.metadata.get('source', '') for doc in result["source_documents"]],
                    "feedback": feedback_type,
                    "comment": feedback_comment or ""
                }
                with open("feedback_log.jsonl", "a") as f:
                    f.write(json.dumps(feedback_data) + "\n")
                st.success("✅ Feedback recorded! Thank you for your input.")

