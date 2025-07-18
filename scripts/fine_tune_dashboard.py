import streamlit as st
import json
import os

st.set_page_config(page_title="Fine-tune Dashboard", layout="wide")
st.title("🛠️ Fine-tune Management Dashboard")

# --- Dataset Review ---
st.header("1. Review Fine-tuning Dataset")
DATASET_PATH = "openai_finetune_ready.jsonl"
if os.path.exists(DATASET_PATH):
    with open(DATASET_PATH) as f:
        lines = f.readlines()
    st.write(f"Total records: {len(lines)}")
    if st.checkbox("Show dataset preview"):
        for i, line in enumerate(lines[:5]):
            st.json(json.loads(line))
    st.download_button("Download Dataset", data="".join(lines), file_name="openai_finetune_ready.jsonl")
else:
    st.warning(f"Dataset file {DATASET_PATH} not found. Run your data prep script first.")

# --- Fine-tune Trigger ---
st.header("2. Trigger Fine-tuning Job")
model_type = st.selectbox("Model Type", ["OpenAI", "Ollama"])
if model_type == "OpenAI":
    api_key = st.text_input("OpenAI API Key", type="password")
    base_model = st.selectbox("Base Model", ["gpt-3.5-turbo-0613"])  # Add more as needed
    if st.button("Start OpenAI Fine-tuning"):
        if not api_key:
            st.error("Please provide your OpenAI API key.")
        else:
            # Placeholder: Replace with backend call
            st.info(f"[SIMULATION] Would trigger OpenAI fine-tuning for {base_model} with {len(lines)} records.")
            st.write("(In production, this would call a backend service or script.)")
elif model_type == "Ollama":
    base_model = st.selectbox("Base Model", ["llama3", "mistral", "phi3"])  # Add more as needed
    if st.button("Start Ollama Fine-tuning"):
        # Placeholder: Replace with backend call
        st.info(f"[SIMULATION] Would trigger Ollama fine-tuning for {base_model} with {len(lines)} records.")
        st.write("(In production, this would call a backend service or script running on a GPU server.)")

# --- Status Area ---
st.header("3. Fine-tuning Job Status")
st.info("This is a placeholder. In production, poll your backend or OpenAI API for job status and show logs/results here.") 