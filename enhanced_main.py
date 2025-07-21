#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.doc_analysis.coordinator import AgentCoordinator
from src.doc_analysis.monitoring_agent import monitoring_agent
from src.doc_analysis.learning_system import AdaptiveLearning
from crewai import Crew, Process
from dotenv import load_dotenv

load_dotenv()

def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found")
        exit(1)
    
    # Initialize systems
    coordinator = AgentCoordinator()
    learning = AdaptiveLearning()
    
    print("🤖 Enhanced Agentic AI System")
    print("1. Collaborative Analysis")
    print("2. System Health Check") 
    print("3. Learning Analysis")
    
    choice = "1"  # Default to collaborative analysis
    print(f"Selected option: {choice}")
    
    if choice == "1":
        query = "Summarize admin portal functionality and test cases"
        enhanced_query = learning.get_query_suggestions(query)
        print(f"📝 Enhanced query: {enhanced_query}")
        
        result = coordinator.collaborative_analysis(enhanced_query)
        print(f"\n🎯 Result: {result}")
        
    elif choice == "2":
        crew = Crew(
            agents=[monitoring_agent],
            tasks=[{
                'description': 'Check system health and provide recommendations',
                'agent': monitoring_agent
            }],
            process=Process.sequential
        )
        result = crew.kickoff()
        print(f"\n🔍 Health Check: {result}")
        
    elif choice == "3":
        improvements = learning.analyze_feedback()
        print(f"\n📊 Learning Insights: {improvements}")

if __name__ == "__main__":
    main()