import requests
import io
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np

load_dotenv()

API_KEY = os.getenv("BYTEME_API_KEY")
BASE_URL = "https://byteme.gendev7.check24.fun/app/api/products/data"
headers = {
    "X-Api-Key": API_KEY
}

def fetch_offers(street, house_number, city, plz):
    """
    Contact ByteMe API and retrieves offers for the given address
    Returns: 
        List[Dict]: A list of raw csv rows as dictionaries
    """
    params = {
    "street":      street,
    "houseNumber": house_number,
    "city":        city,
    "plz":         plz
}
    response = requests.get(BASE_URL, params=params, headers=headers)
    if response.status_code != 200:
        # TODO: change later to exception
        return pd.DataFrame()
    offers = pd.read_csv(io.StringIO(response.text))
    return offers
    # print(response.status_code)

    # csv columns from api response:
    # productId,providerName,speed,monthlyCostInCent,
    # afterTwoYearsMonthlyCost,durationInMonths,connectionType,
    # installationService,tv,limitFrom,maxAge,voucherType,voucherValue

def max_age(row):
    if pd.isna(row['maxAge']):
        return pd.NA
    return int(row['maxAge'])
def voucher_value(row):
    if pd.isna(row['voucherValue']):
        return 0
    return int(row['voucherValue'])
# def max_voucher_value(row):
#     if row['voucherType'] == 'percentage':
#         return int(row['voucherValue']) * row['durationInMonths'] * row['afterTwoYearsMonthlyCost']
#     return int(row['voucherValue'])
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
    offers['name'] = offers['providerName']
    offers['speed_mbps'] = offers['speed'].astype(int)
    offers['cost_eur'] = offers['monthlyCostInCent'].astype(int) / 100
    offers['duration_months'] = offers['durationInMonths'].astype(int)
    offers['post_promo_eur'] = offers['afterTwoYearsMonthlyCost'].astype(int) / 100
    offers['connection_type'] = offers['connectionType']
    offers['installation_included'] = offers['installationService'] == 'true'
    offers['tv'] = offers.apply(tv, axis=1)
    offers['max_age'] = offers.apply(max_age, axis=1)
    offers['voucher_type'] = offers['voucherType']
    offers['voucher_value'] = offers.apply(voucher_value, axis=1)
    # offers['max_voucher_value'] = offers.apply(max_voucher_value, axis=1)
    offers['limit_from'] = offers.apply(limit, axis=1)
    offers['unlimited'] = offers.apply(unlimited, axis=1)

    order = [
        'provider', 'name', 'speed_mbps', 'cost_eur', 'duration_months',
        'post_promo_eur', 'connection_type', 'installation_included', 'tv',
        'max_age', 'voucher_type', 'voucher_value',
        'unlimited', 'limit_from'
    ]
    return offers[order]

def main(street, house_number, city, plz):
    """
    Fetch offers and create a list of parsed dictionaries
    Return:
        Empty list if no offers found
        List[Dict] of parced offers
    """
    offers = fetch_offers(street, house_number, city, plz)
    parsed_offers = transform_offers(offers)
    # if not offers:
    #     return []
    # TODO use pandas instead of dict
    # TODO dict as parameter insted of 4 parameters (street etc)
    return parsed_offers

if __name__ == "__main__":
    df = main("Meisentraße", "7", "Höhenkirchen-Siegertsbrunn", "85635")
    pd.set_option('display.max_columns', None)
    print(df.head()) 
