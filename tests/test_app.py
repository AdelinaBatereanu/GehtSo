import pytest
from unittest.mock import patch

from src.app import app

@pytest.fixture
# Create a test client for the Flask application
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# Tests for the Flask application
# Check if the index page loads correctly
def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"enter your address to start comparing" in response.data.lower()

# Test the /autocomplete endpoint for plz suggestions
def test_autocomplete_plz(client):
    with patch("src.app.autocomplete.fetch_plz_suggestions") as mock_fetch:
        mock_fetch.return_value = [{"display": "10115 Berlin", "postcode": "10115", "city": "Berlin"}]
        response = client.get("/autocomplete?q=1011&field=plz")
        assert response.status_code == 200
        assert b"10115 Berlin" in response.data

# Test if /autocomplete endpint returns and error an invalid (empty) query
def test_autocomplete_invalid(client):
    response = client.get("/autocomplete?q=&field=plz")
    assert response.status_code == 400

# Test the creation and retrieval of a snapshot
def test_share_and_view_snapshot(client):
    # Create a snapshot
    offers = [{"provider": "Test", "name": "Test Offer"}]
    response = client.post("/share", json={"offers": offers, "filters": {}})
    assert response.status_code == 201
    data = response.get_json()
    assert "share_url" in data

    # Extract snapshot_id from URL
    snapshot_id = data["share_url"].split("/")[-1]
    # View the snapshot
    response = client.get(f"/share/{snapshot_id}")
    assert response.status_code == 200
    assert b"Test Offer" in response.data

# Test if /share endpoint returns an error if no offers are provided
def test_share_missing_offers(client):
    response = client.post("/share", json={"filters": {}})
    assert response.status_code == 400