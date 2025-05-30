import pandas as pd
import numpy as np
import asyncio
import pytest
from src.compare_offers import (fill_columns, fetch_offers, 
                                filter_speed, filter_duration, filter_tv, filter_connection_types, 
                                filter_installation, filter_limit, filter_provider, filter_age,
                                sort_by_after_two_years_cost, sort_by_first_years_cost, sort_by_speed
                                )

# ---Test cases for the compare_offers module---
# Test that fetch_offers returns a DataFrame
def test_fetch_offers_returns_dataframes():
    address = {
        "street": "Hauptstrasse",
        "house_number": "5A",
        "plz": "10115",
        "city": "Berlin"
    }
    dfs = asyncio.run(fetch_offers(address))
    assert isinstance(dfs, list)
    for df in dfs:
        assert isinstance(df, pd.DataFrame)

# Test that fill_columns replaces NaN and pd.NA with None
def test_fill_columns_no_nan_or_pdna():
    df = pd.DataFrame({
        "a": [1, np.nan, pd.NA, None],
        "b": [None, "x", np.nan, pd.NA]
    })
    df_filled = fill_columns(df)
    for col in df_filled.columns:
        for val in df_filled[col]:
            assert val is None or not (pd.isna(val)), f"Found {val} in column {col}"

# Test filtering functions
def test_filter_speed():
    df = pd.DataFrame({"speed_mbps": [10, 50, 100]})
    filtered = filter_speed(df, 50)
    assert all(filtered["speed_mbps"] >= 50)
def test_filter_duration():
    df = pd.DataFrame({"duration_months": [12, 24, 36]})
    filtered = filter_duration(df, 24)
    assert all(filtered["duration_months"] <= 24)
def test_filter_tv():
    df = pd.DataFrame({"tv": [None, "TV", None]})
    assert len(filter_tv(df, True)) == 1
    assert len(filter_tv(df, False)) == 2
def test_filter_limit():
    df = pd.DataFrame({"limit_from_gb": [None, 100, 200, np.nan]})
    # Only unlimited offers (None/NaN)
    filtered_none = filter_limit(df, "none")
    assert filtered_none["limit_from_gb"].isna().all()
    # Offers with limit >= 150 or unlimited
    filtered_150 = filter_limit(df, 150)
    assert set(filtered_150["limit_from_gb"].dropna()) == {200}
    assert filtered_150["limit_from_gb"].isna().sum() == 2
    # No filtering
    filtered_all = filter_limit(df)
    assert len(filtered_all) == 4

def test_filter_installation():
    df = pd.DataFrame({"installation_included": [True, False, None]})
    filtered = filter_installation(df, True)
    assert all(filtered["installation_included"] == True)
    assert len(filtered) == 1
    filtered_all = filter_installation(df, False)
    assert len(filtered_all) == 3
def test_filter_connection_types():
    df = pd.DataFrame({"connection_type": ["fiber", "dsl", "cable", "fiber"]})
    filtered = filter_connection_types(df, ["fiber", "dsl"])
    assert set(filtered["connection_type"]) == {"fiber", "dsl"}
    assert len(filtered) == 3
def test_filter_provider():
    df = pd.DataFrame({"provider": ["A", "B", "C", "A"]})
    filtered = filter_provider(df, ["A", "C"])
    assert set(filtered["provider"]) == {"A", "C"}
    assert len(filtered) == 3
def test_filter_age():
    df = pd.DataFrame({"max_age": [18, 25, None, 30]})
    # Should include rows where max_age >= 21 or is None
    filtered = filter_age(df, 21)
    assert set(filtered.index) == {1, 2, 3}
    # If age is None, should return all
    filtered_all = filter_age(df, None)
    assert len(filtered_all) == 4

# Test sorting functions
def test_sort_by_first_years_cost():
    df = pd.DataFrame({"cost_first_years_eur": [30, 20, 50]})
    sorted_df = sort_by_first_years_cost(df)
    assert list(sorted_df["cost_first_years_eur"]) == [20, 30, 50]
    sorted_df_desc = sort_by_first_years_cost(df, ascending=False)
    assert list(sorted_df_desc["cost_first_years_eur"]) == [50, 30, 20]
def test_sort_by_after_two_years_cost():
    df = pd.DataFrame({"after_two_years_eur": [60, 40, 80]})
    sorted_df = sort_by_after_two_years_cost(df)
    assert list(sorted_df["after_two_years_eur"]) == [40, 60, 80]
    sorted_df_desc = sort_by_after_two_years_cost(df, ascending=False)
    assert list(sorted_df_desc["after_two_years_eur"]) == [80, 60, 40]
def test_sort_by_speed():
    df = pd.DataFrame({"speed_mbps": [100, 50, 200]})
    sorted_df = sort_by_speed(df)
    assert list(sorted_df["speed_mbps"]) == [200, 100, 50]
    sorted_df_desc = sort_by_speed(df, ascending=True)
    assert list(sorted_df_desc["speed_mbps"]) == [50, 100, 200]