from dotenv import load_dotenv
import os
import time
import hmac
import hashlib
import requests
import json
import pandas as pd
import numpy as np

load_dotenv() 
CLIENT_ID = os.getenv("PINGPERFECT_CLIENT_ID")
SIGNATURE_SECRET = os.getenv("PINGPERFECT_SIGNATURE_SECRET")

BASE_URL = "https://pingperfect.gendev7.check24.fun/internet/angebote/data"

def sign_payload(json_body, timestamp, secret):
    """
    Sign the payload using HMAC SHA256.
    Args:
        json_body (str): The JSON body to sign.
        timestamp (int): The current timestamp (UNIX time).
        secret (str): The secret key for signing.
    Returns:
        str: The HMAC signature.
    """
    message = f"{timestamp}:{json_body}"
    hm = hmac.new(
        key=secret.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return hm.hexdigest()

def fetch_ping_perfect(address, wants_fiber):
    """
    Fetch offers from the Ping Perfect API for a given address.
    Args:
        address (dict): keys: "street", "plz", "house_number", "city".
        wants_fiber (bool): Whether to fetch fiber offers or not.
    """
    payload = {
        "street": address["street"],
        "plz": address["plz"],
        "houseNumber": address["house_number"],
        "city": address["city"],
        "wantsFiber": wants_fiber
    }
    # Concatenate the timestamp and the request body string with : as a separator.
    json_body = json.dumps(payload, separators=(",", ":"))
    timestamp = int(time.time())
    signature = sign_payload(json_body, timestamp, SIGNATURE_SECRET)

    headers = {
        "X-Client-Id": CLIENT_ID,
        "X-Timestamp": str(timestamp),
        "X-Signature": signature,
        "Content-Type": "application/json"
    }

    response = requests.post(BASE_URL, headers=headers, data=json_body, timeout=10)
    response.raise_for_status()
    results = response.json()
    return results

def transform_offer(offer):
    """
    Transform the offer data into a normalized format.
    Args: offer (dict): with the following keys:
            providerName (str):
            productInfo (dict):
                - speed (int)
                - contractDurationInMonths (int)
                - connectionType (str)
                - tv (str)
                - limitFrom (int)
                - maxAge (int)
            pricingDetails (dict):
                - monthlyCostInCent (int)
                - installationService (str): "yes" or "no"
    Returns:
        dict: A dictionary with the following keys:
            provider, name, speed_mbps, cost_eur (float), duration_months,
            connection_type, installation_included, tv, max_age,
            limit_from, is_unlimited
    """
    info = offer["productInfo"]
    pricing = offer["pricingDetails"]
    return {
        "provider":             "Ping Perfect",
        "name":                 offer["providerName"],
        "speed_mbps":           info["speed"],
        "cost_eur":             float(pricing["monthlyCostInCent"]) / 100,
        "duration_months":      info["contractDurationInMonths"],
        "connection_type":      info["connectionType"].lower(),
        "installation_included": pricing["installationService"] != "no",
        "tv":                   info.get("tv"),
        "max_age":              info.get("maxAge") if info.get("maxAge") else np.nan,
        "limit_from":           info.get("limitFrom") if info.get("limitFrom") else np.nan,
        "is_unlimited":         False if info.get("limitFrom") else True
    }

def main(address):
    """
    Fetch and transform offers for a given address.
    Args:
        address (dict): {
            "street": str,
            "plz": str,
            "house_number": str,
            "city": str
        }
    Returns:
        pd.DataFrame
    """
    # fetch fiber and non-fiber offers separately
    fiber_offers = fetch_ping_perfect(address, True)
    non_fiber_offers = fetch_ping_perfect(address, False)
    # create one list of offers
    offers = fiber_offers + non_fiber_offers

    normalized_offers = []
    for offer in offers:
        normalized = transform_offer(offer)
        normalized_offers.append(normalized)
        
    df = pd.DataFrame(normalized_offers)
    return df

if __name__ == "__main__":

    address = {
        "street": "Meisenstrasse",
        "plz": "85635",
        "house_number": "7",
        "city": "Höhenkirchen-Siegertsbrunn",
    }

    df = main(address)
    pd.set_option('display.max_columns', None)
    print(df.head(15))