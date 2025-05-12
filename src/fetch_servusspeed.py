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
    offers = []
    for pid in product_ids:
        raw = fetch_details(pid, address)
        normalized = transform_offer(raw)
        offers.append(normalized)

    return offers

if __name__ == "__main__":
    test_address = {
        "strasse": "Hauptstraße",
        "hausnummer": "5A",
        "postleitzahl": "10115",
        "stadt": "Berlin",
        "land": "DE"
    }
    all_offers = main(test_address)
    print("All normalized offers:", all_offers)