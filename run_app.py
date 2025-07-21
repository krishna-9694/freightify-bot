#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.doc_analysis.tasks import summarize_documents_task
from crewai import Crew, Process
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found. Please set it in your .env file.")
        exit(1)
    
    print("🚀 Running Document Summarizer...")
    query = "Summarize the admin portal functionality and rate sheet upload process"
    
    crew = Crew(
        agents=[summarize_documents_task.agent],
        tasks=[summarize_documents_task],
        process=Process.sequential
    )
    
    result = crew.kickoff(inputs={"query": query})
    print("\n📄 Summary Result:\n", result)