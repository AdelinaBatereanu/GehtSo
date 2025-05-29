import os, requests
from requests.auth import HTTPBasicAuth
from aiohttp import BasicAuth
import asyncio
import aiohttp
import pandas as pd
import numpy as np

from dotenv import load_dotenv
load_dotenv()

USER = os.getenv("SERVUSSPEED_USERNAME")
PASS = os.getenv("SERVUSSPEED_PASSWORD")

BASE_URL = "https://servus-speed.gendev7.check24.fun"

def fetch_available_products(address):
    """
    Fetch a llist of available product IDs for a given address.
    Takes around 10-15 seconds to complete.
    Args:
        address (dict): {
                        "strasse": str,
                        "hausnummer": str,
                        "postleitzahl": str,
                        "stadt": str,
                        "land": str
                    }
    Returns:
        list: A list of available product IDs.
    """
    url = BASE_URL + "/api/external/available-products"
    auth = HTTPBasicAuth(USER, PASS)
    payload = {"address": address}

    try:
        resp = requests.post(url, json=payload, auth=auth, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.Timeout:
        print("Servus Speed available-products request timed out.")
        return []
    product_ids = data.get("availableProducts")
    if not isinstance(product_ids, list):
        raise ValueError(f"Expected list of IDs, got {product_ids!r}")
    return product_ids

async def fetch_details(session, product_id, address, semaphore):
    """
    Fetch details for a given product ID.
    When called separately, a request takes 10-15 seconds to complete.
    When called in parallel, the time taken grows to around 30-40 seconds depending on the number of requests.
    Args:
        session (aiohttp.ClientSession): The aiohttp session to use for the request.
        product_id (str): The product ID to fetch details for.
        address (dict): The address to use for the request.
        semaphore (asyncio.Semaphore): Semaphore to limit concurrent requests.
    Returns:
        dict: The details of the product.
    """
    url = BASE_URL + "/api/external/product-details/" + product_id
    auth = BasicAuth(USER, PASS)
    payload = {"address": address}

    async with semaphore:
        # print(f"Fetching details for product {product_id}")
        try:
            async with session.post(url, json=payload, auth=auth) as resp:
                resp.raise_for_status()
                return await resp.json()
        except asyncio.TimeoutError:
            print(f"Timeout fetching details for product {product_id}")
            return None

async def fetch_all_offers(product_ids, address):
    """
    Fetch details for all product IDs in parallel.
    Takes around 2 minutes to complete.
    Args:
        product_ids (list): A list of product IDs to fetch details for.
        address (dict): The address to use for the request.
    Returns:
        List[Dict]: A list where each element is a dict with the key
            "servusSpeedProduct", whose value is a dict containing:
                providerName (str)
                productInfo (dict): with keys
                    - speed (int)
                    - contractDurationInMonths (int)
                    - connectionType (str)
                    - tv (str)
                    - limitFrom (int)
                    - maxAge (int)
                pricingDetails (dict): with keys
                    - monthlyCostInCent (int)
                    - installationService (bool)
                discount (int): fixed amount in cents
    """
    semaphore = asyncio.Semaphore(5)
    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [fetch_details(session, pid, address, semaphore) for pid in product_ids]
        try:
            return await asyncio.gather(*tasks)
        except asyncio.TimeoutError:
            print("Servus Speed product-details requests timed out.")
            return []

"""
Note: when using the function below, the time taken to fetch all offers is around 3-4 minutes.

def fetch_offers(product_ids, address):
    offers = []
    for pid in product_ids:
        try:
            print(f"Fetching offer for product {pid}")
            offer = fetch_details(pid, address)
            offers.append(offer)
        except Exception as e:
            print(f"Error fetching {pid}: {e}")
            offers.append(None)
    return offers
"""

def transform_offer(offer):
    """
    Transform the offer data into expected format
    Args:
        List[Dict]: A list where each element is a dict with the key
            "servusSpeedProduct", whose value is a dict containing:
                providerName (str)
                productInfo (dict): with keys
                    - speed (int)
                    - contractDurationInMonths (int)
                    - connectionType (str)
                    - tv (str)
                    - limitFrom (int)
                    - maxAge (int)
                pricingDetails (dict): with keys
                    - monthlyCostInCent (int)
                    - installationService (bool)
                discount (int): fixed amount in cents
        Returns: 
            dict: A dictionary with the following keys:
                provider, name, speed_mbps, cost_eur, voucher_fixed_eur, 
                promo_price_eur, duration_months, connection_type, installation_included,
                tv, limit_from_gb, is_unlimited, max_age
                """
    product = offer["servusSpeedProduct"]
    info = product["productInfo"]
    pricing = product["pricingDetails"]

    data = {}
    data["provider"] = "Servus Speed"
    data["name"] = product["providerName"]
    data["speed_mbps"] = info["speed"]
    data["cost_eur"] = float(pricing["monthlyCostInCent"]) / 100
    # searce for the discount (fixed amount in cents)
    # promo_price_eur = cost_eur - voucher apllied over 24 months
    voucher = product.get("discount")
    data["voucher_fixed_eur"] = (float(voucher) / 100) if voucher else np.nan
    data["promo_price_eur"] = (data["cost_eur"] - data["voucher_fixed_eur"] / 24) if voucher else data["cost_eur"]
    
    data["duration_months"] = info["contractDurationInMonths"]
    data["connection_type"] = info["connectionType"].lower()
    data["installation_included"] = pricing["installationService"]
    data["tv"] = info.get("tv")
    # searches for the limit and sets the unlimited flag
    data["limit_from_gb"] = info["limitFrom"] if info["limitFrom"] is not None else np.nan
    
    data["max_age"] = int(info.get("maxAge"))
    return data

def get_offers(address_input):
    """
    Fetch and transform offers for a given address.
    Args:
        address_input = {
            "street": str,
            "house_number": str,
            "plz": str,
            "city": str,
        }
    Returns:
        pandas.DataFrame
    """
    address = {
        "strasse": address_input["street"],
        "hausnummer": address_input["house_number"],
        "postleitzahl": address_input["plz"],
        "stadt": address_input["city"],
        "land": "DE"
    }

    product_ids = fetch_available_products(address)
    # print(f"Found {len(product_ids)} product IDs")
    print(f"Fetching offers for Servus Speed")
    offers = asyncio.run(fetch_all_offers(product_ids, address))
    normalized_offers = []
    for offer in offers:
        normalized = transform_offer(offer)
        normalized_offers.append(normalized)
    df = pd.DataFrame(normalized_offers)
    print(f"Fetched {len(df)} offers for Servus Speed")
    return df

if __name__ == "__main__":
    test_address = {
        "street": "Hauptstraße",
        "house_number": "5A",
        "plz": "10115",
        "city": "Berlin"
    }
    df = get_offers(test_address)
    pd.set_option('display.max_columns', None)
    print(df.head(20))
