"""
    Tests
"""
import pytest
from app import create_app

@pytest.fixture
def client():
    """
        Test client
    """
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_root_status_code(client):
    """
        Test status code
    """
    response = client.get("/")
    assert response.status_code == 200

def test_root_content(client):
    """
        Test content
    """
    response = client.get("/")
    assert b"Hello, World!" in response.data
