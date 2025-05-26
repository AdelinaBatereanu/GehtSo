from dotenv import load_dotenv
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)
from fetch_byteme import get_offers as get_byteme_offers
from fetch_pingperfect import get_offers as get_pingperfect_offers
from fetch_servusspeed import get_offers as get_servusspeed_offers
from fetch_verbyndich import get_offers as get_verbyndich_offers
from fetch_webwunder import get_offers as get_webwunder_offers
import asyncio
import time
import nest_asyncio
nest_asyncio.apply()
import logging
import numpy as np


MAX_RETRIES = 3
RETRY_BACKOFF = 5  # seconds

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

async def fetch_offers(address):
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, safe_get_offers, get_byteme_offers, address, "ByteMe"),
        loop.run_in_executor(None, safe_get_offers, get_pingperfect_offers, address, "Ping Perfect"),
        loop.run_in_executor(None, safe_get_offers, get_servusspeed_offers, address, "Servus Speed"),
        loop.run_in_executor(None, safe_get_offers, get_verbyndich_offers, address, "Verbyndich"),
        loop.run_in_executor(None, safe_get_offers, get_webwunder_offers, address, "WebWunder"),
    ]
    return await asyncio.gather(*tasks)

    # loop = asyncio.get_event_loop()
    # df_byteme, df_pingperfect, df_servusspeed, df_verbyndich, df_webwunder = loop.run_until_complete(fetch_offers(address))
def get_all_offers(address): 
    df_byteme, df_pingperfect, df_servusspeed, df_verbyndich, df_webwunder = asyncio.run(fetch_offers(address))   
    all_offers = pd.concat(
        [df_byteme, df_pingperfect, df_servusspeed, df_verbyndich, df_webwunder],
        ignore_index=True
    )
    # all_offers["installation_included"] = all_offers["installation_included"].fillna(False).astype("boolean")

    # all_offers["cost_first_years_eur"] = all_offers["promo_price_eur"].fillna(all_offers["cost_eur"])
    # all_offers["after_two_years_eur"] = all_offers["after_two_years_eur"].fillna(all_offers["cost_eur"])

    # all_offers["is_unlimited"] = all_offers["is_unlimited"].fillna(True).astype("boolean")
    # all_offers = all_offers.where(pd.notnull(all_offers), None)
    # all_offers = all_offers.replace({np.nan: None})
    return all_offers

def fill_columns(df):
    required_columns = [
        "cost_first_years_eur", "promo_price_eur", "cost_eur", "after_two_years_eur",
        "installation_included", "is_unlimited", "speed_mbps", "max_age", "duration_months",
        "tv", "limit_from_gb", "connection_type", "provider", "name"
    ]
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    # Fill cost_first_years_eur and after_two_years_eur as before
    df["cost_first_years_eur"] = df["promo_price_eur"].fillna(df["cost_eur"])
    df["after_two_years_eur"] = df["after_two_years_eur"].fillna(df["cost_eur"])
    df["installation_included"] = df["installation_included"].fillna(False).astype("boolean")
    df["is_unlimited"] = df["is_unlimited"].fillna(True).astype("boolean")
    df = df.where(pd.notnull(df), None)
    df = df.replace({np.nan: None})
    return df

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
    address = {
        "street": "Hauptstrasse",
        "house_number": "5A",
        "plz": "10115",
        "city": "Berlin"
    }
    all_offers = get_all_offers(address)
    debug_df = all_offers.applymap(mark_missing)
    debug_df.to_csv("df_check.csv", index=False)
    # pd.set_option('display.max_columns', None)
    # all_offers = get_all_offers()
    # filtered = filter_installation(all_offers, True)
    # print("=== Cheapest DSL Offers ===")
    # print(sort_by_first_years_cost(filtered).head(10))

#TODO: check that all inputs are made safe for api
#TODO: change None to N/A or np.nan
#TODO: add retry mechanisms where needed
#TODO: delete unlimited columns
#TODO: add error handling
#TODO: check requirements