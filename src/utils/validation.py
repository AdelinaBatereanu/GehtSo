import requests
import os
import json

NOMINATIM_URL = os.getenv("NOMINATIM_URL")
HEADERS = json.loads(os.getenv("HEADERS"))

# --- Address Validation ---
def validate_address(street, house_number, plz, city):
    """
    Returns True if the address exists according to Nominatim, else False.
    """
    params = {
        "street": f"{house_number} {street}",
        "city": city,
        "postalcode": plz,
        "countrycodes": "de",
        "format": "json",
        "limit": 1
    }
    resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS)
    resp.raise_for_status()
    results = resp.json()
    return bool(results)