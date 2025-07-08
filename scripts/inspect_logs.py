import os
import sqlite3
from langchain.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()  # Load .env with OPENAI_API_KEY

VECTOR_DIR = "vectorstore"
DB_FILE = "agent_logs.db"

def show_recent_logs(db_path=DB_FILE, limit=10):
    print("\n🔍 Recent Agent Logs (from SQLite):\n" + "-" * 50)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        logs = cursor.fetchall()
        for i, (timestamp, message) in enumerate(logs, 1):
            print(f"\n[{i}] Timestamp: {timestamp}\nMessage:\n{message}\n" + "-"*50)
        conn.close()
    except Exception as e:
        print(f"⚠️ Failed to read logs: {e}")

def inspect_chroma_chunks(vector_dir=VECTOR_DIR, limit=5):
    print("\n📄 Stored Chunks in Chroma Vector DB:\n" + "-" * 50)
    try:
        vectordb = Chroma(
            persist_directory=vector_dir,
            embedding_function=OpenAIEmbeddings()
        )
        chunks = vectordb._collection.get()['documents']
        total_size = 0
        for i, chunk in enumerate(chunks[:limit]):
            size = len(chunk)
            total_size += size
            print(f"\n[{i+1}] Chunk Size: {size} chars\nContent:\n{chunk}\n" + "-"*50)

        print(f"\n✅ Total Chunks: {len(chunks)}")
        print(f"🧠 Total Characters in Top {limit} Chunks: {total_size}")
    except Exception as e:
        print(f"⚠️ Failed to load vector store: {e}")

def get_folder_size(path):
    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total

def show_storage_usage():
    print("\n💾 Storage Usage:\n" + "-" * 50)
    if os.path.exists(VECTOR_DIR):
        vector_size = get_folder_size(VECTOR_DIR)
        print(f"📦 Chroma Vector Store: {vector_size / 1024:.2f} KB")
    else:
        print("📦 Chroma Vector Store: Not found")

    if os.path.exists(DB_FILE):
        db_size = os.path.getsize(DB_FILE)
        print(f"🗃️ SQLite Log DB: {db_size / 1024:.2f} KB")
    else:
        print("🗃️ SQLite Log DB: Not found")

if __name__ == "__main__":
    show_recent_logs(limit=10)
    inspect_chroma_chunks(limit=5)
    show_storage_usage()
