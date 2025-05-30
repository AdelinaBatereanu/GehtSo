import pytest
from src.utils import make_api_safe, str2bool, fetch_plz_suggestions, fetch_street_suggestions, validate_address

# --- Utility Functions ---
# Make sure special characters are URL-safe for API requests
def test_make_api_safe():
    assert make_api_safe("München") == "Munchen"
    assert make_api_safe("Straße 1") == "Strasse+1"
    assert make_api_safe("Café & Bar") == "Cafe+%26+Bar"

# String to boolean conversion
@pytest.mark.parametrize("val,expected", [
    ("true", True),
    ("True", True),
    ("1", True),
    ("false", False),
    ("0", False),
    ("no", False),
    ("yes", True),
    (True, True),
    (False, False),
])
def test_str2bool(val, expected):
    assert str2bool(val) == expected

# --- Address Suggestions ---
# Test fetching postal code suggestions
def test_fetch_plz_suggestions(monkeypatch):
    # Mock requests.get to return a fake response
    class MockResponse:
        def raise_for_status(self): pass
        def json(self):
            return [
                {"address": {"postcode": "10115", "city": "Berlin"}},
                {"address": {"postcode": "10117", "city": "Berlin"}}
            ]
    monkeypatch.setattr("src.utils.requests.get", lambda *a, **kw: MockResponse())
    results = fetch_plz_suggestions("1011")
    assert {"display": "10115 Berlin", "postcode": "10115", "city": "Berlin"} in results
    assert {"display": "10117 Berlin", "postcode": "10117", "city": "Berlin"} in results

# Test fetching street suggestions
def test_fetch_street_suggestions(monkeypatch):
    class MockResponse:
        def raise_for_status(self): pass
        def json(self):
            return [
                {"address": {"road": "Hauptstrasse"}},
                {"address": {"road": "Nebenstrasse"}}
            ]
    monkeypatch.setattr("src.utils.requests.get", lambda *a, **kw: MockResponse())
    results = fetch_street_suggestions("Haupt", "Berlin")
    assert {"display": "Hauptstrasse"} in results
    assert {"display": "Nebenstrasse"} in results
    
# Test address validation
def test_validate_address(monkeypatch):
    class MockResponse:
        def raise_for_status(self): pass
        def json(self): return [{}]
    monkeypatch.setattr("src.utils.requests.get", lambda *a, **kw: MockResponse())
    assert validate_address("Hauptstrasse", "5A", "10115", "Berlin") is True

    class MockResponseEmpty:
        def raise_for_status(self): pass
        def json(self): return []
    monkeypatch.setattr("src.utils.requests.get", lambda *a, **kw: MockResponseEmpty())
    assert validate_address("Fake", "1", "00000", "Nowhere") is False