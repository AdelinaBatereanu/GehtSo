import requests 
from dotenv import load_dotenv
import os
import re
import pandas as pd
from utils import make_api_safe

load_dotenv()
API_KEY = os.getenv("VERBYNDICH_API_KEY")

BASE_URL = "https://verbyndich.gendev7.check24.fun/check24/data"

def fetch_verbyndich_page(address, page):
    params = {
            "apiKey": API_KEY,
            "page": page,
        }
    response = requests.post(BASE_URL, params=params, data=address, allow_redirects=False, timeout=10)  
    response.raise_for_status()
    return response.json()

def fetch_all_offers(address):
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
    data = {}
    m = re.search(r"Für nur (\d+)€ im Monat", desc)
    if m:
        data["cost_eur"] = float(m.group(1))
    m = re.search(r"(\w+)-Verbindung", desc)
    if m:
        data["connection_type"] = m.group(1).lower()
    m = re.search(r"einer Geschwindigkeit von (\d+) Mbit/s", desc)
    if m: 
        data["speed_mbps"] = int(m.group(1))
    m = re.search(r"Zusätzlich sind folgende Fernsehsender enthalten (\w+)\.", desc)
    if m:
        data["tv"] = m.group(1)
    m = re.search(r"Mindestvertragslaufzeit (\d+) Monate", desc)
    if m:
        data["duration_months"] = int(m.group(1))
    m = re.search(r"nur für Personen unter (\d+) Jahren", desc)
    if m:
        data["max_age"] = int(m.group(1))
    m = re.search(r"Ab (\d+)GB pro Monat wird die Geschwindigkeit gedrosselt", desc)
    if m:
        data["limit_from_mbps"] = int(m.group(1))
        data["unlimited"] = False
    else: 
        data["unlimited"] = True
    m = re.search(r"Rabatt beträgt (\d+)€", desc)
    if m:
        data["voucher_fixed"] = float(m.group(1))
    m = re.search(r"monatliche Rechnung bis zum (\d+)\. Monat", desc)
    if m:
        data["promo_duration_months"] = int(m.group(1))
    m = re.search(r"einen Rabatt von (\d+)%", desc)
    if m:
        data["voucher_percent"] = int(m.group(1))
        if data["cost_eur"] * data["voucher_percent"] /100 * data["promo_duration_months"] < data["voucher_fixed"]:
            data["promo_price"] = data["cost_eur"] - data["cost_eur"] * data["voucher_percent"] / 100
        else: 
            data["promo_price"] = data["cost_eur"] - data["voucher_fixed"] / data["promo_duration_months"]
    m = re.search(r"Monat beträgt der monatliche Preis (\d+)€", desc)
    if m:
        data["after_two_years_eur"] = float(m.group(1))
    return data

def transform_offers(all_offers, provider="VerbynDich"):
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
    offers = fetch_all_offers(address)
    # print(offers[:20])
    df = transform_offers(offers)
    return df
        
if __name__ == "__main__":
    address = make_api_safe("Meisenstrasse;7;Höhenkirchen-Siegertsbrunn;85635")
    # print(address)
    df = main(address)
    pd.set_option('display.max_columns', None)
    print(df.head(10))
