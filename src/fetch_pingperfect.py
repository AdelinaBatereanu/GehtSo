from dotenv import load_dotenv
import os
import time
import hmac
import hashlib
import requests
import json

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

fetch_ping_perfect("Meisenstrasse", "85635", "7", "Höhenkirchen-Siegertsbrunn", True)