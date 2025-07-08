import os
import requests
import json
from crewai.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()

@tool("Fetch and Embed Jira Issue")
def fetch_and_embed_jira_issue(issue_id: str) -> str:
    """
    Fetches a Jira issue and embeds it into Chroma vector DB if not already embedded.
    Returns the embedded content or retrieved content.
    """
    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_USER_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    if not all([base_url, email, api_token]):
        return "❌ Missing Jira credentials in environment."

    vectordb = Chroma(
        persist_directory="vectorstore",
        embedding_function=OpenAIEmbeddings()
    )

    # Check if this issue is already embedded
    existing = vectordb.similarity_search(issue_id, k=1)
    if existing and issue_id in existing[0].page_content:
        return f"✅ Retrieved from cache:\n{existing[0].page_content[:500]}"

    # Fetch from Jira API
    auth = (email, api_token)
    url = f"{base_url}/rest/api/3/issue/{issue_id}"
    headers = {"Accept": "application/json"}

    try:
        res = requests.get(url, headers=headers, auth=auth)
        data = res.json()

        summary = data["fields"].get("summary", "")
        description = data["fields"].get("description", {}).get("content", [])
        plain_desc = flatten_jira_description(description)
        status = data["fields"]["status"]["name"]
        labels = ", ".join(data["fields"].get("labels", []))

        content = f"Issue: {issue_id}\nSummary: {summary}\nStatus: {status}\nLabels: {labels}\nDescription:\n{plain_desc}"
        print(f"[INFO] Successfully retrieved Jira issue {issue_id} with status '{status}' and summary: {summary}")
        doc = Document(page_content=content, metadata={"source": f"jira:{issue_id}"})
        print(content)
        vectordb.add_documents([doc])
        vectordb.persist()
        return f"✅ Embedded and stored:\n{content[:500]}"
    except Exception as e:
        return f"❌ Failed to fetch or store Jira issue: {str(e)}"

def flatten_jira_description(desc_blocks):
    parts = []
    for block in desc_blocks:
        for inner in block.get("content", []):
            if "text" in inner:
                parts.append(inner["text"])
    return " ".join(parts)[:3000]