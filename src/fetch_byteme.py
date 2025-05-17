import requests
import io
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np

load_dotenv()
API_KEY = os.getenv("BYTEME_API_KEY")
headers = {"X-Api-Key": API_KEY}

BASE_URL = "https://byteme.gendev7.check24.fun/app/api/products/data"

def fetch_offers(address):
    """
    Contacts ByteMe API and retrieves offers for the given address, drops duplicates
    Args:
        address (dict): {
                        "street":      street (str),
                        "houseNumber": house_number (str),
                        "city":        city (str),
                        "plz":         plz (str)
                        }    
    Returns: 
        pandas.DataFrame with the following columns:
        productId, providerName, speed, monthlyCostInCent,
        afterTwoYearsMonthlyCost, durationInMonths, connectionType,
        installationService, tv, limitFrom, maxAge, voucherType, voucherValue
    """
    response = requests.get(BASE_URL, params=address, headers=headers)
    # print(response.status_code)
    response.raise_for_status()
    offers = pd.read_csv(io.StringIO(response.text))
    offers.drop_duplicates(inplace=True)
    return offers

# The following functions return the value of the column if it is not NaN, otherwise return np.nan
def get_max_age(row):
    if pd.isna(row['maxAge']):
        return np.nan
    return int(row['maxAge'])
def get_voucher_value(row):
    if pd.isna(row['voucherValue']):
        return np.nan
    return int(row['voucherValue'])
def get_limit(row):
    if pd.isna(row['limitFrom']):
        return np.nan
    return int(row['limitFrom'])
def is_unlimited(row):
    if pd.isna(row['limitFrom']):
        return True
    return False
def get_tv(row):
    if pd.isna(row['tv']):
        return pd.NA
    return row['tv']

def transform_offers(offers):
    """
    The function renames columns and converts data types to match the expected output format.
    Args:
        offers (pandas.DataFrame): DataFrame with the following columns:
            productId, providerName, speed, monthlyCostInCent,
            afterTwoYearsMonthlyCost, durationInMonths, connectionType,
            installationService, tv, limitFrom, maxAge, voucherType, voucherValue
    Returns:
        pandas.DataFrame with the following columns:
        provider, product_id, name, speed_mbps, cost_eur, promo_price_eur,
        duration_months, after_two_years_eur, connection_type,
        installation_included, tv, max_age, voucher_fixed_eur,
        voucher_percent, unlimited, limit_from_gb
    """
    offers['provider'] = 'ByteMe'
    offers['product_id'] = offers['productId']
    offers['name'] = offers['providerName']
    offers['speed_mbps'] = offers['speed'].astype(int)
    offers['cost_eur'] = offers['monthlyCostInCent'].astype(float) / 100
    offers['duration_months'] = offers['durationInMonths'].astype(int)
    offers['after_two_years_eur'] = offers['afterTwoYearsMonthlyCost'].astype(float) / 100
    offers['connection_type'] = offers['connectionType'].str.lower()
    offers['installation_included'] = offers['installationService'] == 'true'
    offers['tv'] = offers.apply(get_tv, axis=1)
    offers['max_age'] = offers.apply(get_max_age, axis=1)
    
    # Applies mask to the column 'voucherType'
    # If the type is 'percentage', it applies the function get_voucher_value to the column 'voucher_percentage'
    # promo_price_eur is calculated as cost_eur - (cost_eur * voucher_percent / 100)
    mask = offers['voucherType'] == 'percentage'
    offers.loc[mask, 'voucher_percent'] = offers.loc[mask].apply(get_voucher_value, axis=1)
    offers.loc[mask, 'voucher_fixed_eur'] = np.nan
    offers.loc[mask, 'promo_price_eur'] = offers.loc[mask, 'cost_eur'] - (offers.loc[mask, 'cost_eur'] * offers.loc[mask, 'voucher_percent'] / 100)

    # If the type is not 'percentage', it applies the function get_voucher_value to the column 'voucher_fixed_eur'
    # promo_price_eur is calculated as cost_eur - (voucher_fixed_eur / 24), where 24 is the number of months
    offers.loc[~mask, 'voucher_fixed_eur'] = offers.loc[~mask].apply(get_voucher_value, axis=1) / 100
    offers.loc[~mask, 'voucher_percent'] = np.nan
    offers.loc[~mask, 'promo_price_eur'] = offers.loc[~mask, 'cost_eur'] - (offers.loc[~mask, 'voucher_fixed_eur']) / 24

    offers['limit_from_gb'] = offers.apply(get_limit, axis=1).astype(int)
    offers['unlimited'] = offers.apply(is_unlimited, axis=1)

    order = [
        'provider', 'product_id', 'name', 'speed_mbps', 'cost_eur', 'promo_price_eur', 'duration_months',
        'after_two_years_eur', 'connection_type', 'installation_included', 'tv',
        'max_age', 'voucher_fixed_eur', 'voucher_percent',
        'unlimited', 'limit_from_gb'
    ]
    return offers[order]

def fetch_byteme(address):
    """
    Fetches offers and creates a pandas.DataFrame with the offers in standardized format
    Args: 
        address (dict): {
                        "street":      street (str),
                        "houseNumber": house_number (str),
                        "city":        city (str),
                        "plz":         plz (str)
                        }    
    Return:
        pandas.DataFrame: A DataFrame with the offers
    """
    offers = fetch_offers(address)
    parsed_offers = transform_offers(offers)
    df = pd.DataFrame(parsed_offers)
    return df

if __name__ == "__main__":
    address = {
        "street":      "Meisentraße",
        "houseNumber": "7",
        "city":        "Höhenkirchen-Siegertsbrunn",
        "plz":         "85635"
    }
    df = fetch_byteme(address)
    pd.set_option('display.max_columns', None)
    print(df.head(20)) 

    