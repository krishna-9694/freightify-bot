from src.doc_analysis.tasks import summarize_documents_task, generate_test_cases_task, test_api_endpoints_task, extract_and_store_jira_issue_task
from crewai import Crew, Process
import os
from dotenv import load_dotenv
load_dotenv()

def get_user_choice():
    print("Choose an agent to run:")
    print("1. Document Summarizer")
    print("2. Test Case Generator")
    print("3. API Tester")
    print("4. Jira Extractor")
    return input("Enter 1 or 2 or 3 or 4: ").strip()

def get_query():
    return input("Enter your query or prompt: ").strip()

if __name__ == "__main__":
    try:
        if not os.getenv("OPENAI_API_KEY"):
            print("❌ OPENAI_API_KEY not found. Please set it in your .env file.")
            exit(1)

        choice = get_user_choice()
        
        if choice in ["1", "2"]:
            query = get_query()
            if not query.strip():
                print("❌ Query cannot be empty.")
                exit(1)

        if choice == "1":
            crew = Crew(
                agents=[summarize_documents_task.agent],
                tasks=[summarize_documents_task],
                process=Process.sequential
            )
            result = crew.kickoff(inputs={"query": query})
            print("\n📄 Summary Result:\n", result)

        elif choice == "2":
            crew = Crew(
                agents=[generate_test_cases_task.agent],
                tasks=[generate_test_cases_task],
                process=Process.sequential
            )
            result = crew.kickoff(inputs={"query": query})
            print("\n🧪 Test Case Scenarios:\n", result)
        
        elif choice == "3":
            crew = Crew(
                agents=[test_api_endpoints_task.agent],
                tasks=[test_api_endpoints_task],
                process=Process.sequential
            )
            result = crew.kickoff(inputs={})

        elif choice == "4":
            issue_id = input("Enter Jira issue ID (e.g., JIRA-123): ").strip()
            if not issue_id:
                print("❌ Issue ID cannot be empty.")
                exit(1)
            crew = Crew(
                agents=[extract_and_store_jira_issue_task.agent],
                tasks=[extract_and_store_jira_issue_task],
                process=Process.sequential
            )
            result = crew.kickoff(inputs={"issue_id": issue_id})

        else:
            print("❌ Invalid choice. Please run again and enter 1, 2, 3, or 4.")
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        exit(1)