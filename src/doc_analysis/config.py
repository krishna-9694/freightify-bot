import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Model Configuration
    MODEL_TYPE = os.getenv("MODEL_TYPE", "openai").lower()
    
    # Vector Store Paths
    VECTORSTORE_OPENAI = "vectorstore_openai"
    VECTORSTORE_OLLAMA = "vectorstore_ollama" 
    VECTORSTORE_NOMIC = "vectorstore_nomic"
    
    # Document Folder
    DOC_FOLDER = "common"
    
    # Jira Configuration
    JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
    JIRA_USER_EMAIL = os.getenv("JIRA_USER_EMAIL")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    
    # API Testing
    TOKEN_CACHE_PATH = os.getenv("TOKEN_CACHE_PATH", ".token_cache.json")
    
    @classmethod
    def get_vectorstore_path(cls, model_type: str = None) -> str:
        model_type = model_type or cls.MODEL_TYPE
        if model_type == "openai":
            return cls.VECTORSTORE_OPENAI
        elif model_type == "ollama":
            return cls.VECTORSTORE_OLLAMA
        else:
            return cls.VECTORSTORE_NOMIC