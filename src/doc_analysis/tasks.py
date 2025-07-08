from crewai import Task
from src.doc_analysis.agents import document_summarizer, test_case_generator, api_tester, jira_connector_agent

summarize_documents_task = Task(
    description="""
Based on the user's query, analyze and summarize the key information from the documents 
located in the common folder. Highlight any process, decision, or policy relevant to the query.
""",
    expected_output="""
A 2–3 paragraph summary addressing the user's query with references to relevant content.
""",
    agent=document_summarizer
)

generate_test_cases_task = Task(
    description="""
Review all the documents located in the common folder thoroughly and extract steps. Based on these, create detailed 
test case scenarios that could validate. Include both happy path and edge case testing ideas.
""",
    expected_output="""
At least 10 detailed test cases. Each should include:
- Title
- Steps
- Expected result
- Any assumptions
""",
    agent=test_case_generator
)

test_api_endpoints_task = Task(
    description="""
    Load and parse the carrier JSON from the `api_specs/` folder.

    For each endpoint defined in the OpenAPI document:
        - Identify the HTTP method (GET, POST, PUT, DELETE)
        - Construct appropriate request inputs:
        - Query parameters for GET
        - JSON payload for POST/PUT based on request schema
        - Inject authorization headers (OAuth2 Bearer token and x-api-key)
        - Execute the request using the provided base URL
        - Handle and log success and failure cases (2xx, 4xx, 5xx)

    Ensure that tests include:
        - Valid request scenarios (expected success)
        - Invalid or edge-case requests (expected error codes)

    This test should simulate how a real client would interact with the API using authentication, headers, and payloads.""",
    expected_output="""
        Return a structured report of all API test attempts.

        For each endpoint tested, include:
            - HTTP method and full request URL
            - Status code returned
            - Request payload or parameters used
            - Authorization headers included
            - Response body (truncated to 300 characters)
            - Pass/Fail interpretation

    Clearly distinguish successful requests from failures and summarize the overall test coverage.""",
    agent=api_tester
)

extract_and_store_jira_issue_task = Task(
    description="""
    Given a Jira issue ID, fetch the issue from the Jira API.
    Extract summary, status, labels, and description.
    Embed the issue content into the vector store if not already present.
    If already stored, retrieve it from Chroma for reuse.
    """,
    expected_output="""
    A preview of the issue content and a confirmation that it was embedded or retrieved from cache.
    """,
    agent=jira_connector_agent
)
