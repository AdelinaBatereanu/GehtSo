from dotenv import load_dotenv
import os
import time
import hmac
import hashlib
import requests
import json
import pandas as pd

load_dotenv() 
client_id = os.getenv("PINGPERFECT_CLIENT_ID")
signature_secret = os.getenv("PINGPERFECT_SIGNATURE_SECRET")

def sign_payload(json_body, timestamp, secret):
    message = f"{timestamp}:{json_body}"
    hm = hmac.new(
        key=secret.encode('utf-8'),
        msg=message.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return hm.hexdigest()

def fetch_ping_perfect(street, plz, house_number, city, wants_fiber):

    payload = {
        "street": street,
        "plz": plz,
        "houseNumber": house_number,
        "city": city,
        "wantsFiber": wants_fiber
    }

    json_body = json.dumps(payload, separators=(",", ":"))
    timestamp = int(time.time())
    signature = sign_payload(json_body, timestamp, signature_secret)

    headers = {
        "X-Client-Id": client_id,
        "X-Timestamp": str(timestamp),
        "X-Signature": signature,
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://pingperfect.gendev7.check24.fun/internet/angebote/data",
        headers=headers,
        data=json_body,
        timeout=10
    )
    response.raise_for_status()
    results = response.json()
    print(results[:5])
    return results

def transform_offer(offer):
    # product = offer["providerName"]
    info = offer["productInfo"]
    pricing = offer["pricingDetails"]
    return {
        "name": offer["providerName"],
        "speed_mbps":           info["speed"],
        "cost_eur":             float(pricing["monthlyCostInCent"]) / 100,
        "duration_months":      info["contractDurationInMonths"],
        "connection_type":      info["connectionType"],
        "installation_included": pricing["installationService"] != "no",
        "tv":                   info.get("tv"),
        "max_age_limit":        info.get("maxAge"),
        "limit_from":           info.get("limitFrom"),
        "is_unlimited":         True if info.get("limitFrom") else False
    }
# TODO: change None to N/A for pandas

def main(street, plz, house_number, city):
    fiber_offers = fetch_ping_perfect(street, plz, house_number, city, True)
    non_fiber_offers = fetch_ping_perfect(street, plz, house_number, city, False)
    offers = fiber_offers + non_fiber_offers
    normalized_offers = []
    for offer in offers:
        normalized = transform_offer(offer)
        normalized_offers.append(normalized)
    df = pd.DataFrame(normalized_offers)
    print(df.head())
    return df

main("Meisenstrasse", "85635", "7", "Höhenkirchen-Siegertsbrunn")