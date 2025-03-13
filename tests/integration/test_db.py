import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.db.init_db import init_db, init_vector_db, initialize_all_databases
from app.core.app_config import INSERT_MOCK_DATA

@patch("psycopg2.connect")
def test_init_vector_db(mock_connect):
    """Test vector database initialization."""
    # Setup mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    
    # Call the function
    init_vector_db()
    
    # Verify the connection was established with correct parameters
    mock_connect.assert_called_with(
        dbname="vector_db",
        user="postgres",
        password="password",
        host="pgvector-db",
        port="5432"
    )
    
    # Verify necessary SQL commands were executed
    mock_cursor.execute.assert_any_call("BEGIN;")
    mock_cursor.execute.assert_any_call("CREATE EXTENSION IF NOT EXISTS vector;")
    
    # Verify the transaction was committed
    mock_conn.commit.assert_called_once()
    
    # Verify resources were cleaned up
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@pytest.mark.asyncio
async def test_init_db():
    """Test database schema initialization."""
    # Use AsyncMock for async operations
    with patch("app.db.init_db.engine") as mock_engine:
        # Setup mock connection with AsyncMock
        mock_conn = AsyncMock()
        mock_engine.begin.return_value.__aenter__.return_value = mock_conn
        
        # Set up AsyncMock for the run_sync method
        mock_conn.run_sync = AsyncMock()
        
        # Call the function
        await init_db()
        
        # Verify the database schema was created
        mock_conn.run_sync.assert_called_once()

@pytest.mark.asyncio
async def test_initialize_all_databases():
    """Test initialization of all databases."""
    # Use AsyncMock for async operations
    with patch("app.db.init_db.init_db", new_callable=AsyncMock) as mock_init_db, \
         patch("app.db.init_db.init_vector_db") as mock_init_vector_db:
        
        # Call the function
        await initialize_all_databases()
        
        # Verify both initialization functions were called
        mock_init_db.assert_called_once()
        mock_init_vector_db.assert_called_once()
