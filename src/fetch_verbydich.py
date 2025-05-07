import requests 
from dotenv import load_dotenv
import os

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

if __name__ == "__main__":
    all_offers = fetch_all_offers(address)
    print(all_offers[:5])