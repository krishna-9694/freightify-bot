from crewai import Agent
from src.doc_analysis.tools.db_logger import log_to_db
from src.doc_analysis.tools.rag_vector_tool import retrieve_context_from_docs
from src.doc_analysis.tools.api_test_runner import test_apis_from_spec
from src.doc_analysis.tools.jira_fetcher import fetch_and_embed_jira_issue


#from src.doc_analysis.tools.read_all_files import read_folder_contents

# tools = [read_folder_contents]  # This is the tool object
# #agent = Agent(tools=tools)

# #tools = [read_folder_contents, another_tool, ...] # This is for multi tool object usage

# document_summarizer = Agent(
#     role='Intelligent Content Summarizer',
#     goal='Summarize key points from documents based on a user’s query',
#     backstory="You are a senior documentation analyst skilled in synthesizing insights from complex internal documents.",
#     tools=[read_folder_contents, log_to_db],
#     verbose=True,
#     memory=True
# )

# test_case_generator = Agent(
#     role='Quality Tester and Scenario Generator',
#     goal='Generate test case scenarios based on workflows found in documentation',
#     backstory="You are a QA engineer who understands systems and edge cases and can translate them into solid test cases.",
#     tools=[read_folder_contents, log_to_db],
#     verbose=True,
#     memory=True
# )

document_summarizer = Agent(
    role='Intelligent Content Summarizer',
    goal='Summarize content relevant to the query from internal documentation',
    backstory="You're a senior knowledge specialist who answers context-aware questions and skilled in synthesizing insights from complex internal documents.",
    tools=[retrieve_context_from_docs, log_to_db],
    verbose=True,
    memory=True
)

test_case_generator = Agent(
    role='QA Test Case Engineer',
    goal='Generate detailed test cases based on documentation and workflows',
    backstory="You're a QA agent that understands systems through document comprehension and edge cases and can translate them into solid test cases.",
    tools=[retrieve_context_from_docs, log_to_db],
    verbose=True,
    memory=True
)

api_tester = Agent(
    role='API QA Specialist',
    goal='Ensure APIs are functionally correct by analyzing and testing endpoints.',
    backstory="You specialize in API testing and validate status codes, responses, and schemas.",
    tools=[test_apis_from_spec, log_to_db],
    verbose=True,
    memory=True
)

jira_connector_agent = Agent(
    role='Jira Issue Retriever',
    goal='Fetch Jira issue content and embed it into the vector DB',
    backstory="You specialize in integrating with Jira, extracting issue details, and preparing them for future LLM analysis.",
    tools=[fetch_and_embed_jira_issue, log_to_db],
    verbose=True,
    memory=True
)