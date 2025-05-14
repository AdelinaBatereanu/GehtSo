import requests 
from dotenv import load_dotenv
import os
import re
import pandas as pd

load_dotenv()
BASE_URL = "https://verbyndich.gendev7.check24.fun/check24/data"
API_KEY = os.getenv("VERBYNDICH_API_KEY")

# TODO: check for umlaut (encode utf-8)
address = "Meisenstrasse;7;Hohenkirchen-Siegertsbrunn;85635"

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
        data["connection_type"] = m.group(1)
        # TODO: make all connection types the same format (lowercase, english)
    m = re.search(r"einer Geschwindigkeit von (\d+) Mbit/s", desc)
    if m: 
        data["speed_mbps"] = int(m.group(1))
    m = re.search(r"Mindestvertragslaufzeit (\d+) Monate", desc)
    if m:
        data["duration_months"] = int(m.group(1))
    m = re.search(r"Ab (\d+)GB pro Monat wird die Geschwindigkeit gedrosselt", desc)
    if m:
        data["limit_from"] = int(m.group(1))
    m = re.search(r"einen Rabatt von (\d+)%", desc)
    if m:
        data["voucher_value"] = int(m.group(1))
    m = re.search(r"monatliche Rechnung bis zum (\d+)\. Monat", desc)
    if m:
        data["promo_duration_months"] = int(m.group(1))
    m = re.search(r"Rabatt beträgt (\d+)€", desc)
    if m:
        data["max_discount_eur"] = float(m.group(1))
    m = re.search(r"Ab dem 24\. Monat beträgt der monatliche Preis (\d+)€", desc)
    if m:
        data["post_promo_eur"] = float(m.group(1))
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
    raw = fetch_all_offers(address)
    df = transform_offers(raw)
    print(df.head())
        
if __name__ == "__main__":
    main(address)