import os
from typing import List, Optional
from langchain.schema import Document
from langchain_openai import ChatOpenAI
import requests

class SimpleAgentCoordinator:
    """A lightweight agent coordinator that works without CrewAI dependencies"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")
    
    def collaborative_analysis(self, query: str, mode: str = "balanced") -> str:
        """Perform analysis using available LLMs without CrewAI dependencies
        
        Args:
            query: The prompt to analyze
            mode: Analysis mode - "summary", "testing", or "balanced"
            
        Returns:
            Analysis result as text
        """
        # Try OpenAI first
        if self.openai_key:
            try:
                model = "gpt-4" if mode == "balanced" else "gpt-3.5-turbo"
                llm = ChatOpenAI(model=model, temperature=0)
                
                # Adjust prompt based on mode
                if mode == "summary":
                    query += "\n\nFocus on providing a comprehensive summary of the key information."
                elif mode == "testing":
                    query += "\n\nFocus on creating detailed test scenarios and validation approaches."
                
                return llm.invoke(query)
            except Exception as e:
                print(f"OpenAI analysis failed: {str(e)}")
                # Fall back to Gemini
        
        # Try Gemini if OpenAI fails or is not available
        if self.gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_key}"
                
                # Adjust prompt based on mode
                if mode == "summary":
                    query += "\n\nFocus on providing a comprehensive summary of the key information."
                elif mode == "testing":
                    query += "\n\nFocus on creating detailed test scenarios and validation approaches."
                
                data = {"contents": [{"parts": [{"text": query}]}]}
                response = requests.post(url, json=data)
                result = response.json()
                
                if "candidates" in result:
                    return result["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    return f"Error from Gemini API: {result.get('error', {}).get('message', 'Unknown error')}"
            except Exception as e:
                print(f"Gemini analysis failed: {str(e)}")
        
        # Fallback message if both fail
        return "Unable to perform analysis. Please check your API keys for OpenAI or Gemini."

class SimpleAdaptiveLearning:
    """A lightweight learning system that works without CrewAI dependencies"""
    
    def get_query_suggestions(self, query: str) -> str:
        """Enhance the query with additional context or clarifications
        
        Args:
            query: The original user query
            
        Returns:
            Enhanced query
        """
        # Simple enhancement without requiring external dependencies
        enhanced_query = query
        
        # Add specificity to general questions
        if any(word in query.lower() for word in ["what", "how", "explain"]):
            enhanced_query += " Please provide specific details and examples."
        
        # Add request for process steps to workflow questions
        if any(word in query.lower() for word in ["process", "workflow", "steps"]):
            enhanced_query += " Include the step-by-step process and any important considerations."
        
        return enhanced_query