"""Tests"""
import pytest
from app import create_app

@pytest.fixture
def client():
    """Test client"""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client

def test_root_status_code(test_client):
    """Test status code"""
    response = test_client.get("/")
    assert response.status_code == 200

def test_root_content(test_client):
    """Test content"""
    response = test_client.get("/")
    assert b"Hello, World!" in response.data
