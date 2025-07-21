from crewai import Crew, Process
from .agents import document_summarizer, test_case_generator, api_tester

class AgentCoordinator:
    def __init__(self):
        self.agents = {
            'summarizer': document_summarizer,
            'tester': test_case_generator,
            'api_tester': api_tester
        }
    
    def collaborative_analysis(self, query: str, mode="balanced"):
        """Multi-agent collaborative workflow
        
        Args:
            query: The user's question or request
            mode: Analysis mode - "summary" (focus on summarization), 
                  "testing" (focus on test cases), or "balanced" (both)
        """
        if mode == "summary":
            crew = Crew(
                agents=[self.agents['summarizer']],
                tasks=[self._create_summary_task(query)],
                process=Process.sequential
            )
        elif mode == "testing":
            crew = Crew(
                agents=[self.agents['tester']],
                tasks=[self._create_test_task(query)],
                process=Process.sequential
            )
        else:  # balanced mode
            crew = Crew(
                agents=[self.agents['summarizer'], self.agents['tester']],
                tasks=[
                    self._create_summary_task(query),
                    self._create_test_task(query)
                ],
                process=Process.sequential
            )
        return crew.kickoff(inputs={"query": query})
    
    def _create_summary_task(self, query):
        from .tasks import summarize_documents_task
        return summarize_documents_task
    
    def _create_test_task(self, query):
        from .tasks import generate_test_cases_task
        return generate_test_cases_task