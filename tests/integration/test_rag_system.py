import pytest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from app.llm.rag import BaseRAGSystem, RAGSystem_PDF, RAGSystem_JSON

@pytest.fixture
def mock_pdf_file():
    # Create a temporary PDF file for testing
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(b"%PDF-1.5\n%Test PDF Content")
        return tmp_file.name

@pytest.fixture
def mock_json_file():
    # Create a temporary JSON file for testing
    data = {
        "patients": [
            {
                "id": 1,
                "name": "John Doe",
                "age": 45,
                "diagnosis": "Hypertension",
                "medications": ["Lisinopril", "Amlodipine"]
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "age": 35,
                "diagnosis": "Type 2 Diabetes",
                "medications": ["Metformin", "Insulin"]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w+", delete=False) as tmp_file:
        json.dump(data, tmp_file)
        return tmp_file.name

@pytest.fixture
def cleanup_files(mock_pdf_file, mock_json_file):
    yield
    # Clean up temporary files
    if os.path.exists(mock_pdf_file):
        os.unlink(mock_pdf_file)
    if os.path.exists(mock_json_file):
        os.unlink(mock_json_file)

@pytest.mark.asyncio
async def test_base_rag_system():
    """Test basic functions of the BaseRAGSystem."""
    # Initialize the base RAG system
    rag_system = BaseRAGSystem()
    
    # Test clear_state
    rag_system.conversation_state = {"test": "data"}
    rag_system.clear_state()
    assert rag_system.conversation_state == {}
    
    # Test similar method
    similarity = rag_system.similar("hello", "hello there")
    assert 0 < similarity < 1  # Should be similar but not identical
    
    similarity = rag_system.similar("hello", "hello")
    assert similarity == 1.0  # Should be identical

@pytest.mark.asyncio
async def test_rag_query_no_documents():
    """Test querying when no documents have been indexed."""
    rag_system = BaseRAGSystem()
    response = await rag_system.query_model("What is hypertension?")
    assert response == "No documents have been indexed yet."

@patch("app.llm.rag.OllamaEmbeddings")
@patch("app.llm.rag.PGVector")
@patch("app.llm.rag.PyPDFLoader")
@pytest.mark.asyncio
async def test_pdf_rag_system(mock_pdf_loader, mock_pgvector, mock_embeddings, mock_pdf_file, cleanup_files):
    """Test the PDF RAG system with mocked components."""
    # Mock the necessary components
    mock_pdf_loader.return_value.load.return_value = [MagicMock()]
    mock_pgvector.from_documents.return_value = MagicMock()
    
    # Configure the mocked vectorstore
    mock_vectorstore = MagicMock()
    mock_retriever = MagicMock()
    mock_retriever.__or__ = MagicMock(return_value=MagicMock())
    mock_vectorstore.as_retriever.return_value = mock_retriever
    mock_pgvector.from_documents.return_value = mock_vectorstore
    
    # Patch the LLM initialization to avoid external service calls
    with patch("app.llm.rag.init_replicate") as mock_init_replicate:
        mock_llm = MagicMock()
        mock_init_replicate.return_value = mock_llm
        
        # Test PDF indexing
        with patch("langchain.hub.pull") as mock_hub_pull:
            mock_hub_pull.return_value = MagicMock()
            
            # Initialize the RAG system with our test PDF
            rag_system = RAGSystem_PDF(mock_pdf_file)
            
            # Verify the components were called correctly
            mock_pdf_loader.assert_called_with(mock_pdf_file)
            mock_pgvector.from_documents.assert_called_once()
            mock_vectorstore.as_retriever.assert_called_once()
            
            # Verify the RAG chain was created
            assert rag_system.rag_chain is not None

@patch("app.llm.rag.OllamaEmbeddings")
@patch("app.llm.rag.PGVector")
@patch("app.llm.rag.JSONLoader")
@pytest.mark.asyncio
async def test_json_rag_system(mock_json_loader, mock_pgvector, mock_embeddings, mock_json_file, cleanup_files):
    """Test the JSON RAG system with mocked components."""
    # Mock the necessary components
    mock_json_loader.return_value.load.return_value = [MagicMock()]
    mock_pgvector.from_documents.return_value = MagicMock()
    
    # Configure the mocked vectorstore
    mock_vectorstore = MagicMock()
    mock_retriever = MagicMock()
    mock_retriever.__or__ = MagicMock(return_value=MagicMock())
    mock_vectorstore.as_retriever.return_value = mock_retriever
    mock_pgvector.from_documents.return_value = mock_vectorstore
    
    # Patch the LLM initialization to avoid external service calls
    with patch("app.llm.rag.init_replicate") as mock_init_replicate:
        mock_llm = MagicMock()
        mock_init_replicate.return_value = mock_llm
        
        # Test JSON indexing
        with patch("langchain.hub.pull") as mock_hub_pull:
            mock_hub_pull.return_value = MagicMock()
            
            # Initialize the RAG system with our test JSON
            rag_system = RAGSystem_JSON(mock_json_file)
            
            # Verify the components were called correctly
            mock_json_loader.assert_called_with(mock_json_file, jq_schema=".patients[]", text_content=False)
            mock_pgvector.from_documents.assert_called_once()
            mock_vectorstore.as_retriever.assert_called_once()
            
            # Verify the RAG chain was created
            assert rag_system.rag_chain is not None
