import pytest
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_redirect(client):
    """Test that the index page redirects to the dashboard"""
    response = client.get('/')
    assert response.status_code == 302
    assert '/dashboard' in response.location or response.location.endswith('/')
