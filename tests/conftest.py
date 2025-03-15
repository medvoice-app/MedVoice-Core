import asyncio
import os
import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import pytest_asyncio
from typing import AsyncGenerator, Generator

# Override environment settings for testing
os.environ["TESTING"] = "1"

# Import after environment settings so they take effect
from app.core.app_config import INSERT_MOCK_DATA, ON_LOCALHOST
from app.main import app
from app.db.session import get_db, engine
from app.models.nurse import Nurse
from app.utils.passwd_helpers import get_password_hash
from app.schemas.nurse import NurseRegister
from app.crud import crud_nurse

# Test database URL - use SQLite for testing with a unique file name per session to avoid conflicts
TEST_DATABASE_URL = f"sqlite+aiosqlite:///./test_{uuid.uuid4().hex}.db"

# Create test engine
test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    test_engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@pytest_asyncio.fixture(scope="session")
async def setup_test_db():
    """Create test database tables"""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Nurse.metadata.create_all)
        
    yield
    
    # Drop tables after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Nurse.metadata.drop_all)
    
    # Remove database file
    db_file = TEST_DATABASE_URL.replace("sqlite+aiosqlite:///", "")
    if os.path.exists(db_file):
        os.remove(db_file)

@pytest_asyncio.fixture
async def db_session(setup_test_db) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for tests"""
    async with TestingSessionLocal() as session:
        # Start with a clean state for each test
        try:
            yield session
            # Roll back changes made during the test
            await session.rollback()
        finally:
            await session.close()

@pytest.fixture
def client(event_loop, db_session) -> Generator[TestClient, None, None]:
    """Create a test client with database session override"""
    # Define the dependency override function that uses our test db session
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session is closed by the db_session fixture

    app.dependency_overrides[get_db] = override_get_db
    
    # Use TestClient with the app that has overridden dependencies
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up the overrides after the test
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def test_nurse(db_session) -> dict:
    """Create a test nurse and return the details."""
    # Create a unique email to avoid conflicts
    unique_email = f"test_{uuid.uuid4().hex}@example.com"
    
    nurse_data = NurseRegister(
        name="Test Nurse",
        email=unique_email,
        password="testpassword"  # Plain password
    )
    
    # Create nurse with hashed password
    hashed_nurse_data = NurseRegister(
        name=nurse_data.name,
        email=nurse_data.email,
        password=get_password_hash(nurse_data.password)
    )
    
    nurse = await crud_nurse.create_nurse(db_session, hashed_nurse_data)
    await db_session.commit()
    
    return {
        "id": nurse.id,
        "name": nurse.name,
        "email": nurse.email,
        "password": "testpassword"  # Return plain password for testing
    }

# Replace the custom event_loop fixture with a fixture that configures the event loop policy
import pytest
import asyncio

# Instead of redefining event_loop, define an event_loop_policy fixture
@pytest.fixture(scope="session")
def event_loop_policy():
    """Return the event loop policy to use."""
    return asyncio.get_event_loop_policy()
