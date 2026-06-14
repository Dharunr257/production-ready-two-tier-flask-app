import pytest
from app import app

@pytest.fixture
def client():
    """Configures the Flask application in testing mode and yields a test client."""
    app.config['TESTING'] = True
    # Disable CSRF or cookie security issues during unit testing if any
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Verifies that the GET /health endpoint returns a 200 OK status code and correct JSON payload."""
    response = client.get('//health')
    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy"}

def test_home_page_load(client):
    """Verifies that the index home page loads correctly, even if database is offline (DevOps resilience)."""
    response = client.get('/')
    assert response.status_code == 200
    # Asserts that the template rendered the container layout
    assert b"Employee Directory" in response.data
