import requests
import csv
import io
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("BYTEME_API_KEY")
BASE_URL = "https://byteme.gendev7.check24.fun/app/api/products/data"
headers = {
    "X-Api-Key": API_KEY
}

def fetch_offers(street, house_number, city, plz):
    """
    Contact ByteMe API and retrieves offers for the given address
    Returns: 
        List[Dict]: A list of raw csv rows as dictionaries
    """
    params = {
    "street":      street,
    "houseNumber": house_number,
    "city":        city,
    "plz":         plz
}
    response = requests.get(BASE_URL, params=params, headers=headers)
    if response.status_code != 200:
        # TODO: change later to exception
        return []
    text_stream = io.StringIO(response.text)
    reader = csv.DictReader(text_stream)
    # print(response.status_code)
    return list(reader)

def parse_offer(offer):
    """
    Convert a raw CSV row dict into a fully typed offer dict. 
    """
    name = offer["providerName"]
    speed = int(offer["speed"])
    cost_in_cent = int(offer["monthlyCostInCent"])
    cost = cost_in_cent / 100
    duration = int(offer["durationInMonths"])
    post_promo_in_cent = int(offer["afterTwoYearsMonthlyCost"])
    post_promo_cost = post_promo_in_cent / 100
    connection_type = offer["connectionType"]
    installation = offer["installationService"]
    installation = True if installation == "true" else False
    tv = offer["tv"]
    max_age = offer["maxAge"]
    max_age = int(max_age) if max_age else None
    voucher_type = offer["voucherType"]
    voucher_value = offer["voucherValue"]
    voucher_value = int(voucher_value) if voucher_value else 0
    if voucher_value == 0:
        voucher_desc = ""     # no voucher
    elif voucher_type == "percentage":
        voucher_desc = f"{voucher_value}% off"
    else:
        voucher_desc = f"{voucher_value} ({voucher_type})" # in case voucher_type not "percentage"
    unlimited = False if offer["limitFrom"] else True
    return {
        "name": name,
        "speed_mbps": speed,
        "cost_eur": cost,
        "voucher": voucher_desc,
        "duration_months": duration,
        "post_promo_cost_eur": post_promo_cost,
        "connection_type": connection_type,
        "installation_included": installation,
        "tv": tv,
        "max_age_limit": max_age,
        "is_unlimited": unlimited
    }

def main(street, house_number, city, plz):
    """
    Fetch offers and create a list of parsed dictionaries
    Return:
        Empty list if no offers found
        List[Dict] of parced offers
    """
    raw = fetch_offers(street, house_number, city, plz)
    if not raw:
        return []
    # TODO use pandas instead of dict
    # TODO dict as parameter insted of 4 parameters (street etc)
    return [parse_offer(r) for r in raw]

if __name__ == "__main__":
    main("Meisentraße", "7", "Höhenkirchen-Siegertsbrunn", "85635")