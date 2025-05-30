import pandas as pd
import pytest
from src.providers import fetch_byteme, fetch_pingperfect, fetch_servusspeed, fetch_verbyndich, fetch_webwunder

ADDRESS = {
    "street": "Hauptstrasse",
    "house_number": "5A",
    "plz": "10115",
    "city": "Berlin"
}

@pytest.mark.parametrize("provider_func", [
    fetch_byteme.get_offers,
    fetch_pingperfect.get_offers,
    fetch_servusspeed.get_offers,
    fetch_verbyndich.get_offers,
    fetch_webwunder.get_offers,
])
# Test that each provider function returns a DataFrame with minimal expected columns
def test_provider_returns_dataframe(provider_func):
    df = provider_func(ADDRESS)
    assert isinstance(df, pd.DataFrame)
    # Check for at least some expected columns
    for col in ["provider", "name", "cost_eur", "speed_mbps", 
                "connection_type", "duration_months"
                ]:
        assert col in df.columns