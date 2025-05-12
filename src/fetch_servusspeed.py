from dotenv import load_dotenv
import os, requests
from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

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
    product_ids = data.get("availableProducts")
    if not isinstance(product_ids, list):
        raise ValueError(f"Expected list of IDs, got {product_ids!r}")
    return product_ids       

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

def transform_offer(offer):
    product = offer["servusSpeedProduct"]
    info = product["productInfo"]
    pricing = product["pricingDetails"]
    # TODO: fix voucher problem
    return {
        "name": product["providerName"],
        "speed_mbps":         info["speed"],
        "cost_eur":           float(pricing["monthlyCostInCent"]) / 100,
        # "voucher_eur":        float(pricing.get("discount")) / 100,
        "duration_months":    info["contractDurationInMonths"],
        "connection_type":    info["connectionType"],
        "installation_included": bool(pricing["installationService"]),
        "tv":                  info.get("tv"),        # might be None
        "max_age_limit":       int(info.get("maxAge")),    # might be None
        "is_unlimited":        False  
    }

def main(address):
    product_ids = fetch_available_products(address)
    print(f"Found {len(product_ids)} product IDs")
    offers = fetch_offers(product_ids, address)
    normalized_offers = []
    for offer in offers:
        normalized = transform_offer(offer)
        normalized_offers.append(normalized)
    df = pd.DataFrame(normalized_offers)
    print(df.head())
    return df

if __name__ == "__main__":
    test_address = {
        "strasse": "Hauptstraße",
        "hausnummer": "5A",
        "postleitzahl": "10115",
        "stadt": "Berlin",
        "land": "DE"
    }
    main(test_address)