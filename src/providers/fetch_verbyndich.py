import os
import re
import asyncio
import aiohttp
import pandas as pd
import numpy as np

from .base import ProviderFetcher

from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("VERBYNDICH_API_KEY")

BASE_URL = "https://verbyndich.gendev7.check24.fun/check24/data"

async def fetch_offers_from_page(session, address, page):
    """
    Async function to fetch offers from a specific page
    """
    params = {
        "apiKey": API_KEY,
        "page": page,
    }
    async with session.post(BASE_URL, params=params, data=address, allow_redirects=False, timeout=10) as response:
        response.raise_for_status()
        return await response.json()

async def fetch_all_offers(address):
    """
    Fetches all offers for the given address from Verbyndich API asynchronously
    """
    print("Fetching offers from Verbyndich API...")
    all_offers = []
    page = 0

    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            data = await fetch_offers_from_page(session, address, page)
            all_offers.append(data)
            while not data["last"]:
                page += 1
                data = await fetch_offers_from_page(session, address, page)
                all_offers.append(data)
        except asyncio.TimeoutError:
            print("Verbyndich API request timed out.")
            return []

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
    data["limit_from_gb"] = int(m.group(1)) if (m := re.search(r"Ab (\d+)GB pro Monat wird die Geschwindigkeit gedrosselt", desc)) else np.nan
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

class VerbynDichFetcher(ProviderFetcher):
    def get_offers(self, address_input):
        """
        Main function to fetch and transform offers from Verbyndich API
        Args:
            address_input = {
                    "street": "Hauptstraße",
                    "house_number": "5A",
                    "plz": "10115",
                    "city": "Berlin"
                }
        Returns:
            pandas.DataFrame: DataFrame with the offers
        """
        address = ";".join([address_input[key] for key in ["street", "house_number", "city", "plz"]])
        offers = asyncio.run(fetch_all_offers(address))
        df = transform_offers(offers)
        print(f"Found {len(df)} offers, Verbyndich")
        return df
        
if __name__ == "__main__":
    address = {
            "street": "Hauptstrasse",
            "house_number": "5A",
            "plz": "10115",
            "city": "Berlin"
        }
    df = VerbynDichFetcher.get_offers(address)
    pd.set_option('display.max_columns', None)
    print(df.head(10))