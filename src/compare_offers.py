import asyncio

import nest_asyncio
nest_asyncio.apply()

import pandas as pd
pd.set_option('future.no_silent_downcasting', True)
import numpy as np

from src.utils.data_access_utils import safe_get_offers

from src.providers.fetch_byteme import ByteMeFetcher
from src.providers.fetch_pingperfect import PingPerfectFetcher
from src.providers.fetch_servusspeed import ServusSpeedFetcher
from src.providers.fetch_verbyndich import VerbynDichFetcher
from src.providers.fetch_webwunder import WebWunderFetcher

async def fetch_offers(address):
    """
    Fetch offers from multiple providers asynchronously.
    Args:
        address (dict): Address to fetch offers for.
    Returns:
        list: List of DataFrames with offers from different providers.
    """
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, safe_get_offers, PingPerfectFetcher().get_offers, address, "Ping Perfect"),
        loop.run_in_executor(None, safe_get_offers, ServusSpeedFetcher.get_offers, address, "Servus Speed"),
        loop.run_in_executor(None, safe_get_offers, VerbynDichFetcher.get_offers, address, "VerbynDich"),
        loop.run_in_executor(None, safe_get_offers, WebWunderFetcher.get_offers, address, "WebWunder"),
        loop.run_in_executor(None, safe_get_offers, ByteMeFetcher.get_offers, address, "ByteMe"),
    ]
    return await asyncio.gather(*tasks)

def fill_columns(df):
    """
    Fill missing columns in the DataFrame with None or default values.
    Args:
        df (pd.DataFrame): DataFrame with offers.
    Returns:
        pd.DataFrame: DataFrame with filled columns.
    """
    required_columns = [
        "cost_first_years_eur", "promo_price_eur", "cost_eur", "after_two_years_eur",
        "voucher_fixed_eur", "voucher_percent",
        "installation_included", "speed_mbps", "max_age", "duration_months",
        "tv", "limit_from_gb", "connection_type", "provider", "name"
    ]
    # Ensure all required columns are present
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    # if no promo price is given, use cost_eur
    df["cost_first_years_eur"] = df["promo_price_eur"].fillna(df["cost_eur"])
    # if the price does not change after two years, use cost_eur
    df["after_two_years_eur"] = df["after_two_years_eur"].fillna(df["cost_eur"])
    # if no information about the installation is given, assume it is not included
    df["installation_included"] = df["installation_included"].fillna(False).astype("boolean")
    # convert np.nan and pd.NA to None
    df = df.where(pd.notnull(df), None)
    df = df.replace({np.nan: None})
    return df

def aggregate_offers(address):
    dfs = asyncio.run(fetch_offers(address))
    all_offers = pd.concat(dfs, ignore_index=True)
    return fill_columns(all_offers)

"""Filtering and sorting functions for offers DataFrame. (not used in the main script, but can be used for further processing)"""

def filter_speed(df, min_speed):
    return df[df["speed_mbps"] >= min_speed]

# def filter_cost(df, max_cost):
#     return df[df["cost_first_years_eur"] <= max_cost]

def filter_duration(df, max_duration):
    return df[df["duration_months"] <= max_duration]

def filter_tv(df, tv_required):
    if tv_required:
        return df[df["tv"].notna()]
    else:
        return df[df["tv"].isna()]
    
def filter_limit(df, min_limit=None):
    if min_limit == "none":
        # Only unlimited offers (limit_from_gb is null/NaN)
        return df[df["limit_from_gb"].isna()]
    elif min_limit is not None:
        # Offers with limit >= min_limit or unlimited
        return df[(df["limit_from_gb"].isna()) | (df["limit_from_gb"] >= min_limit)]
    else:
        # No filtering
        return df
    
def filter_installation(df, installation_required=True):
    if installation_required:
        return df[df["installation_included"] == True]
    else:
        return df

def filter_connection_types(df, connection_types):
    """
    Args: connection_types (list): list of connection types to filter by
    """
    return df[df["connection_type"].isin(connection_types)]

def filter_provider(df, providers):
    """ 
    Args: providers (list): list of provider names to filter by
    """
    return df[df["provider"].isin(providers)]

def filter_age(df, age):
    if age:
        return df[(df["max_age"] >= age) | (df["max_age"].isna())]
    return df

def sort_by_first_years_cost(df, ascending=True):
    return df.sort_values(by="cost_first_years_eur", ascending=ascending)

def sort_by_after_two_years_cost(df, ascending=True):
    return df.sort_values(by="after_two_years_eur", ascending=ascending)

def sort_by_speed(df, ascending=False):
    return df.sort_values(by="speed_mbps", ascending=ascending)

if __name__ == "__main__":
    address = {
        "street": "Hauptstrasse",
        "house_number": "5A",
        "plz": "10115",
        "city": "Berlin"
    }
    all_offers = aggregate_offers(address)
    print(all_offers.head())
    # Save DataFrame to CSV for checking (used for development purposes))
    # all_offers.to_csv("df_check.csv", index=False)