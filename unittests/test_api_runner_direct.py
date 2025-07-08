import os
from dotenv import load_dotenv
from src.doc_analysis.tools.api_test_runner import test_apis_from_spec

# Load .env
load_dotenv()

def main():
    print("🔍 Running API test directly from tool (no CrewAI)...\n")

    result = test_apis_from_spec.run("api_specs/carrier.json")
    print(result)

if __name__ == "__main__":
    main()
