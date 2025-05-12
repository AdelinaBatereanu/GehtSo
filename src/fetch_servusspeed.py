from dotenv import load_dotenv
import os, requests
from requests.auth import HTTPBasicAuth

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

    if resp.status_code == 200:
        data = resp.json()
        return data["availableProducts"]
    else:
        print(f"Error {resp.status_code}: {resp.text}")
        resp.raise_for_status()

def fetch_details(product_id, address):
    url = BASE_URL + "/api/external/product-details/" + product_id
    auth = HTTPBasicAuth(USER, PASS)
    payload = {
        "address": address
    }
    resp = requests.post(url, json=payload, auth=auth)
    print(f"Fetching details for {product_id} → status {resp.status_code}")
    if resp.status_code == 200:
        return resp.json()
    else:
        print("  Response body:", resp.text)
        resp.raise_for_status()

if __name__ == "__main__":
    test_address = {
        "strasse": "Hauptstraße",
        "hausnummer": "5A",
        "postleitzahl": "10115",
        "stadt": "Berlin",
        "land": "DE"
    }
    products = fetch_available_products(test_address)
    data = []
    for product_id in products:
        info = fetch_details(product_id, test_address)
        data.append(info)
    print (data[:5])