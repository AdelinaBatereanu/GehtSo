import pandas as pd
import pytest
from src.providers.fetch_byteme import ByteMeFetcher
from src.providers.fetch_pingperfect import PingPerfectFetcher
from src.providers.fetch_servusspeed import ServusSpeedFetcher
from src.providers.fetch_verbyndich import VerbynDichFetcher
from src.providers.fetch_webwunder import WebWunderFetcher

ADDRESS = {
    "street": "Hauptstrasse",
    "house_number": "5A",
    "plz": "10115",
    "city": "Berlin"
}

@pytest.mark.parametrize("provider_instance", [
    ByteMeFetcher(),
    PingPerfectFetcher(),
    ServusSpeedFetcher(),
    VerbynDichFetcher(),
    WebWunderFetcher(),
])
# Test that each provider function returns a DataFrame with minimal expected columns
def test_provider_returns_dataframe(provider_instance):
    df = provider_instance.get_offers(ADDRESS)
    assert isinstance(df, pd.DataFrame)
    # Check for at least some expected columns
    for col in ["provider", "name", "cost_eur", "speed_mbps", 
                "connection_type", "duration_months"
                ]:
        assert col in df.columns