import requests 
from dotenv import load_dotenv
import os
import re
import pandas as pd
import numpy as np
from utils import make_api_safe

load_dotenv()
API_KEY = os.getenv("VERBYNDICH_API_KEY")

BASE_URL = "https://verbyndich.gendev7.check24.fun/check24/data"

def fetch_verbyndich_page(address, page):
    """
    Contacts Verbyndich API and retrieves offers for the given address
    Args:
        address (str): address in the format "street;house_number;city;plz"
        page (int): page number to fetch
    Returns:
        dict: JSON response from the API
    """
    params = {
            "apiKey": API_KEY,
            "page": page,
        }
    response = requests.post(BASE_URL, params=params, data=address, allow_redirects=False, timeout=10)  
    response.raise_for_status()
    return response.json()

def fetch_all_offers(address):
    """
    Fetches all offers for the given address from Verbyndich API
    """
    all_offers = []
    page = 0
    data = fetch_verbyndich_page(address, page)
    all_offers.append(data)
    while not data["last"]:
        page += 1
        data = fetch_verbyndich_page(address, page)
        all_offers.append(data)
    return all_offers

def parse_description(desc):
    """
    Parses the description of the offer and extracts relevant information
    Args:
        desc (str): description of the offer
    Returns:
        dict: dictionary with extracted information
    """
    data = {}

    data["cost_eur"] = float(m.group(1)) if (m := re.search(r"Für nur (\d+)€ im Monat", desc)) else np.nan
    data["connection_type"] = m.group(1).lower() if (m := re.search(r"(\w+)-Verbindung", desc)) else pd.NA
    data["speed_mbps"] = int(m.group(1)) if (m := re.search(r"einer Geschwindigkeit von (\d+) Mbit/s", desc)) else np.nan
    data["tv"] = m.group(1) if (m := re.search(r"folgende Fernsehsender enthalten (\w+)\.", desc)) else pd.NA
    data["duration_months"] = int(m.group(1)) if (m := re.search(r"Mindestvertragslaufzeit (\d+) Monate", desc)) else np.nan
    data["max_age"] = int(m.group(1)) if (m := re.search(r"nur für Personen unter (\d+) Jahren", desc)) else np.nan
    # searches for the limit and sets the unlimited flag
    limit = re.search(r"Ab (\d+)GB pro Monat wird die Geschwindigkeit gedrosselt", desc)
    if limit:
        data["limit_from_gb"] = int(limit.group(1))
        data["unlimited"] = False
    else: 
        data["limit_from_gb"] = np.nan
        data["unlimited"] = True
    # seaches for the max voucher value and promo duration
    data["voucher_fixed_eur"] = float(m.group(1)) if (m := re.search(r"Rabatt beträgt (\d+)€", desc)) else np.nan
    data["promo_duration_months"] = int(m.group(1)) if  (m := re.search(r"monatliche Rechnung bis zum (\d+)\. Monat", desc)) else np.nan
    # searches for the voucher percent and calculates the promo price
    discount = re.search(r"einen Rabatt von (\d+)%", desc)
    if discount:
        data["voucher_percent"] = int(discount.group(1))
        # if voucher percent applied over voucher duration < max voucher value
        # voucher in percent is used to calculate the promo price
        if data["cost_eur"] * data["voucher_percent"] /100 * data["promo_duration_months"] < data["voucher_fixed_eur"]:
            data["promo_price_eur"] = data["cost_eur"] - data["cost_eur"] * data["voucher_percent"] / 100 
        # if voucher percent applied over voucher duration < max voucher value
        # max voucher value is used to calculate the promo price
        else: 
            data["promo_price_eur"] = data["cost_eur"] - data["voucher_fixed_eur"] / data["promo_duration_months"]

    data["after_two_years_eur"] = float(m.group(1)) if (m := re.search(r"Monat beträgt der monatliche Preis (\d+)€", desc)) else np.nan
    return data

def transform_offers(all_offers, provider="VerbynDich"):
    """
    Transforms the offers into a DataFrame with the required columns
    Args:
        all_offers (list): list of offers from Verbyndich API
        provider (str): name of the provider
    Returns:
        pandas.DataFrame: DataFrame with the following columns:
            provider, name, cost_eur, connection_type, speed_mbps,
            tv, duration_months, max_age, limit_from_gb, unlimited,
            voucher_fixed_eur, promo_duration_months, voucher_percent,
            promo_price_eur, after_two_years_eur
    """
    offers_list = []
    for offer in all_offers:
        if not offer.get("valid", False):
            continue    
        d = {
            "provider": provider,
            "name": offer["product"],
            **parse_description(offer["description"]),
        }
        offers_list.append(d)
    df = pd.DataFrame(offers_list)
    return df

def main(address):
    """
    Main function to fetch and transform offers from Verbyndich API
    Args:
        address (str): address in the format "street;house_number;city;plz"
    Returns:
        pandas.DataFrame: DataFrame with the offers
    """
    offers = fetch_all_offers(address)
    # print(offers[:20])
    df = transform_offers(offers)
    return df
        
if __name__ == "__main__":
    address = make_api_safe("Meisenstrasse;7;Höhenkirchen-Siegertsbrunn;85635")
    df = main(address)
    pd.set_option('display.max_columns', None)
    print(df.head(10))