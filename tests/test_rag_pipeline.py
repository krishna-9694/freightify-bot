import pytest
from unittest.mock import Mock, patch
from src.doc_analysis.tools.rag_vector_tool import retrieve_context_from_docs

class TestRAGPipeline:
    
    @patch('src.doc_analysis.tools.rag_vector_tool.Chroma')
    @patch('src.doc_analysis.tools.rag_vector_tool.OpenAIEmbeddings')
    def test_retrieve_context_success(self, mock_embeddings, mock_chroma):
        # Mock vector store response
        mock_doc = Mock()
        mock_doc.page_content = "Test document content"
        mock_chroma.return_value.similarity_search.return_value = [mock_doc]
        
        result = retrieve_context_from_docs("test query")
        
        assert "Test document content" in result
        mock_chroma.return_value.similarity_search.assert_called_once_with("test query", k=5)
    
    @patch('src.doc_analysis.tools.rag_vector_tool.Chroma')
    def test_retrieve_context_error_handling(self, mock_chroma):
        # Mock exception
        mock_chroma.side_effect = Exception("Vector store error")
        
        result = retrieve_context_from_docs("test query")
        
        assert "Error retrieving context" in result