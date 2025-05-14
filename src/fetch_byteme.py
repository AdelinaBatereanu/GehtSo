import requests
import io
from dotenv import load_dotenv
import os
import pandas as pd
# import numpy as np

load_dotenv()
API_KEY = os.getenv("BYTEME_API_KEY")
headers = {"X-Api-Key": API_KEY}

BASE_URL = "https://byteme.gendev7.check24.fun/app/api/products/data"

def fetch_offers(address):
    """
    Contact ByteMe API and retrieves offers for the given address
    Returns: 
        List[Dict]: A list of raw csv rows as dictionaries
    """
#     address = {
#     "street":      street[str],
#     "houseNumber": house_number[str],
#     "city":        city[str],
#     "plz":         plz[str]
# }    
    
    response = requests.get(BASE_URL, params=address, headers=headers)
    # print(response.status_code)
    response.raise_for_status()
    offers = pd.read_csv(io.StringIO(response.text))
    return offers

"""
csv columns from api response:
productId,providerName,speed,monthlyCostInCent,
afterTwoYearsMonthlyCost,durationInMonths,connectionType,
installationService,tv,limitFrom,maxAge,voucherType,voucherValue
"""

def max_age(row):
    if pd.isna(row['maxAge']):
        return pd.NA
    return int(row['maxAge'])
def voucher_value(row):
    if pd.isna(row['voucherValue']):
        return 0
    return int(row['voucherValue'])
def limit(row):
    if pd.isna(row['limitFrom']):
        return pd.NA
    return int(row['limitFrom'])
def unlimited(row):
    if pd.isna(row['limitFrom']):
        return True
    return False
def tv(row):
    if pd.isna(row['tv']):
        return pd.NA
    return row['tv']

def transform_offers(offers):
    offers['provider'] = 'ByteMe'
    offers['product_id'] = offers['productId']
    offers['name'] = offers['providerName']
    offers['speed_mbps'] = offers['speed'].astype(int)
    offers['cost_eur'] = offers['monthlyCostInCent'].astype(float) / 100
    offers['duration_months'] = offers['durationInMonths'].astype(int)
    offers['after_two_years_eur'] = offers['afterTwoYearsMonthlyCost'].astype(float) / 100
    offers['connection_type'] = offers['connectionType'].str.lower()
    offers['installation_included'] = offers['installationService'] == 'true'
    offers['tv'] = offers.apply(tv, axis=1)
    offers['max_age'] = offers.apply(max_age, axis=1)
    
    mask = offers['voucherType'] == 'percentage'
    offers.loc[mask, 'voucher_percent'] = offers.loc[mask].apply(voucher_value, axis=1)
    offers.loc[mask, 'voucher_fixed_eur'] = pd.NA
    offers.loc[mask, 'promo_price'] = offers.loc[mask, 'cost_eur'] - (offers.loc[mask, 'cost_eur'] * offers.loc[mask, 'voucher_percent'] / 100)

    offers.loc[~mask, 'voucher_fixed_eur'] = offers.loc[~mask].apply(voucher_value, axis=1) / 100
    offers.loc[~mask, 'voucher_percent'] = pd.NA
    offers.loc[~mask, 'promo_price'] = offers.loc[~mask, 'cost_eur'] - (offers.loc[~mask, 'voucher_fixed_eur']) / 24
# TODO: check if 24 is correct (or better duration months)
    offers['limit_from_mbps'] = offers.apply(limit, axis=1).astype(int)
    offers['unlimited'] = offers.apply(unlimited, axis=1)

    order = [
        'provider', 'product_id', 'name', 'speed_mbps', 'cost_eur', 'promo_price', 'duration_months',
        'after_two_years_eur', 'connection_type', 'installation_included', 'tv',
        'max_age', 'voucher_fixed_eur', 'voucher_percent',
        'unlimited', 'limit_from_mbps'
    ]
    return offers[order]

def main(address):
    """
    Fetch offers and create a list of parsed dictionaries
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
    df = main(address)
    pd.set_option('display.max_columns', None)
    print(df.head()) 
