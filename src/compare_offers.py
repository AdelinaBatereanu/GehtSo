from dotenv import load_dotenv
import os
from utils import make_api_safe
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)
from fetch_byteme import get_offers as get_byteme_offers
from fetch_pingperfect import get_offers as get_pingperfect_offers
from fetch_servusspeed import get_offers as get_servusspeed_offers
from fetch_verbydich import get_offers as get_verbyndich_offers
from fetch_webwunder import get_offers as get_webwunder_offers
import asyncio
import time
import logging
import numpy as np


address = {
    "street": "Hauptstrasse",
    "house_number": "5A",
    "plz": "10115",
    "city": "Berlin"
}

MAX_RETRIES = 3
RETRY_BACKOFF = 7  # seconds

def safe_get_offers(get_offers_func, address, provider_name):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return get_offers_func(address)
        except Exception as e:
            logging.error(f"[{provider_name}] Attempt {attempt} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF ** attempt)
            else:
                logging.error(f"[{provider_name}] All retries failed. Returning empty DataFrame.")
                return pd.DataFrame()

async def fetch_offers():
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, safe_get_offers, get_byteme_offers, address, "ByteMe"),
        loop.run_in_executor(None, safe_get_offers, get_pingperfect_offers, address, "Ping Perfect"),
        loop.run_in_executor(None, safe_get_offers, get_servusspeed_offers, address, "Servus Speed"),
        loop.run_in_executor(None, safe_get_offers, get_verbyndich_offers, address, "Verbyndich"),
        loop.run_in_executor(None, safe_get_offers, get_webwunder_offers, address, "WebWunder"),
    ]
    return await asyncio.gather(*tasks)

df_byteme, df_pingperfect, df_servusspeed, df_verbyndich, df_webwunder = asyncio.run(fetch_offers())

def get_all_offers():    
    all_offers = pd.concat(
        [df_byteme, df_pingperfect, df_servusspeed, df_verbyndich, df_webwunder],
        ignore_index=True
    )
    all_offers["installation_included"] = all_offers["installation_included"].fillna(False).astype("boolean")

    all_offers["cost_first_years_eur"] = all_offers["promo_price_eur"].fillna(all_offers["cost_eur"])
    all_offers["after_two_years_eur"] = all_offers["after_two_years_eur"].fillna(all_offers["cost_eur"])

    all_offers["is_unlimited"] = all_offers["is_unlimited"].fillna(True).astype("boolean")
    all_offers = all_offers.where(pd.notnull(all_offers), None)
    all_offers = all_offers.replace({np.nan: None})
    return all_offers

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
    filtered_by_connection = pd.DataFrame()
    for connection_type in connection_types:
        filtered = df[df["connection_type"] == connection_type]
        filtered_by_connection = pd.concat([filtered_by_connection, filtered], ignore_index=True)  
    return filtered_by_connection

def filter_provider(df, providers):
    filtered_by_provider = pd.DataFrame()
    for provider in providers:
        filtered = df[df["provider"] == provider]
        filtered_by_provider = pd.concat([filtered_by_provider, filtered], ignore_index=True)
    return filtered_by_provider

def sort_by_first_years_cost(df, ascending=True):
    return df.sort_values(by="cost_first_years_eur", ascending=ascending)

def sort_by_after_two_years_cost(df, ascending=True):
    return df.sort_values(by="after_two_years_eur", ascending=ascending)

def sort_by_speed(df, ascending=False):
    return df.sort_values(by="speed_mbps", ascending=ascending)

def mark_missing(cell):
    if cell is None:
        return "<<None>>"
    if cell is pd.NA:
        return "<<pd.NA>>"
    # use numpy to detect NaN
    if isinstance(cell, float) and np.isnan(cell):
        return "<<np.nan>>"
    return cell

if __name__ == "__main__":
    # pass
    all_offers = get_all_offers()
    debug_df = all_offers.applymap(mark_missing)
    debug_df.to_csv("df_check.csv", index=False)
    # pd.set_option('display.max_columns', None)
    # all_offers = get_all_offers()
    # filtered = filter_installation(all_offers, True)
    # print("=== Cheapest DSL Offers ===")
    # print(sort_by_first_years_cost(filtered).head(10))

#TODO: check that all inputs are made safe for api
#TODO: change None to N/A or np.nan
#TODO: add timeout
#TODO: add retry mechanisms where needed
#TODO: delete unlimited columns
#TODO: add error handling
#TODO: check requirements