import os
import pytest
from src.doc_analysis.tools.jira_fetcher import fetch_and_embed_jira_issue

@pytest.mark.integration
def test_fetch_and_embed_jira_issue(monkeypatch):
    # Mock credentials for safety
    monkeypatch.setenv("JIRA_BASE_URL", "https://your-domain.atlassian.net")
    monkeypatch.setenv("JIRA_USER_EMAIL", "your.email@company.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "your-token")

    issue_id = "DEV-15402"
    result = fetch_and_embed_jira_issue(issue_id)
    assert "Issue:" in result
    assert "Summary:" in result
    assert "Status:" in result
    assert "Description:" in result
    #assert "Expected summary text" in result
    #assert "Open" in result  # or whatever the expected status is
    print(result)
