import pytest
from fastapi.testclient import TestClient
import uuid

def test_register_nurse(client):
    """Test nurse registration endpoint."""
    # Add unique identifier to email to avoid conflicts
    unique_email = f"new_nurse_{uuid.uuid4().hex[:8]}@example.com"
    
    response = client.post(
        "/api/v1/nurses/register",  # Change back to nurses (plural)
        json={
            "name": "New Nurse",
            "email": unique_email,
            "password": "securepassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Nurse"
    assert data["email"] == unique_email
    assert "password" not in data  # Password should not be returned

def test_register_duplicate_email(client, test_nurse):
    """Test registration with an existing email."""
    response = client.post(
        "/api/v1/nurses/register",  # Change back to nurses (plural)
        json={
            "name": "Duplicate Nurse",
            "email": test_nurse["email"],  # Use existing email
            "password": "securepassword123"
        }
    )
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_success(client, test_nurse):
    """Test successful login."""
    response = client.post(
        "/api/v1/nurses/login",  # Change back to nurses (plural)
        json={
            "email": test_nurse["email"],
            "password": test_nurse["password"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert "nurse_id" in data
    assert data["nurse_id"] == test_nurse["id"]

def test_login_invalid_credentials(client, test_nurse):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/nurses/login",  # Change back to nurses (plural)
        json={
            "email": test_nurse["email"],
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

def test_get_nurses(client, test_nurse):
    """Test getting all nurses."""
    response = client.get("/api/v1/nurses/")  # Change back to nurses (plural)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least one nurse (the test_nurse)
    
    # Find our test nurse in the list
    found_nurse = next((n for n in data if n["id"] == test_nurse["id"]), None)
    assert found_nurse is not None
    assert found_nurse["name"] == test_nurse["name"]
    assert found_nurse["email"] == test_nurse["email"]

def test_get_nurse_by_id(client, test_nurse):
    """Test getting a nurse by ID."""
    response = client.get(f"/api/v1/nurses/{test_nurse['id']}")  # Change back to nurses (plural)
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_nurse["id"]
    assert data["name"] == test_nurse["name"]
    assert data["email"] == test_nurse["email"]

def test_update_nurse(client, test_nurse):
    """Test updating a nurse."""
    unique_email = f"updated_{uuid.uuid4().hex[:8]}@example.com"
    update_data = {
        "name": "Updated Name",
        "email": unique_email
    }
    
    response = client.put(
        f"/api/v1/nurses/{test_nurse['id']}",  # Change back to nurses (plural)
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]

def test_delete_nurse(client, test_nurse):
    """Test deleting a nurse."""
    response = client.delete(f"/api/v1/nurses/{test_nurse['id']}")  # Change back to nurses (plural)
    
    assert response.status_code == 200
    assert response.json() is True
    
    # Verify the nurse is actually deleted
    get_response = client.get(f"/api/v1/nurses/{test_nurse['id']}")
    assert "detail" in get_response.json()
    assert "Nurse not found" in get_response.json()["detail"]
