from dotenv import load_dotenv
import os, requests
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()
USER = os.getenv("SERVUSSPEED_USERNAME")
PASS = os.getenv("SERVUSSPEED_PASSWORD")

BASE_URL = "https://servus-speed.gendev7.check24.fun"

def fetch_available_products(address):
    url = BASE_URL + "/api/external/available-products"
    auth = HTTPBasicAuth(USER, PASS)
    payload = {
        "address": address
    }

    resp = requests.post(url, json=payload, auth=auth)
    resp.raise_for_status()
    data = resp.json()
    return data["availableProducts"]        

def fetch_details(product_id, address):
    url = BASE_URL + "/api/external/product-details/" + product_id
    auth = HTTPBasicAuth(USER, PASS)
    payload = {
        "address": address
    }
    resp = requests.post(url, json=payload, auth=auth)
    resp.raise_for_status()
    return resp.json()

def fetch_offers(product_ids, address, max_workers=5):
    offers = [None] * len(product_ids)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {
            executor.submit(fetch_details, pid, address): idx
            for idx, pid in enumerate(product_ids)
        }
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                offers[idx] = future.result()
            except Exception as e:
                print(f"Error fetching {product_ids[idx]}: {e}")
    return offers
# TODO: compare how much time a requests needs (find library for it)
# TODO: google how ThreadPoolExecutor works

if __name__ == "__main__":
    test_address = {
        "strasse": "Hauptstraße",
        "hausnummer": "5A",
        "postleitzahl": "10115",
        "stadt": "Berlin",
        "land": "DE"
    }
    products = fetch_available_products(test_address)

    # 2) Fetch their details in parallel
    detailed_jsons = fetch_offers(products, test_address, max_workers=5)

    # 3) Just print the first few to verify
    for dj in detailed_jsons[:5]:
        print(dj)