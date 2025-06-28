"""
Test cases for the API
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_item():
    """Test item creation"""
    response = client.post(
        "/items",
        json={"name": "Test Item", "description": "Test Description"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"
    assert response.json()["id"] == 1


def test_get_items():
    """Test getting all items"""
    response = client.get("/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
