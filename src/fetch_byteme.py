import requests
import csv
import io
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("BYTEME_API_KEY")
BASE_URL = "https://byteme.gendev7.check24.fun/app/api/products/data"
params = {
    "street":      "Meisenstraße",
    "houseNumber": "7",
    "city":        "Höhenkirchen-Siegertsbrunn",
    "plz":         "85635"
}
headers = {
    "X-Api-Key": API_KEY
}

def fetch_offers():
    response = requests.get(BASE_URL, params=params, headers=headers)
    if response.status_code != 200:
        return []
    text_stream = io.StringIO(response.text)
    reader = csv.DictReader(text_stream)
    print(response.status_code)
    return list(reader)

def main():
    offers = fetch_offers()
    if not offers:
        print("No offers found")
        return
    for offer in offers:
        name = offer["providerName"]
        speed = int(offer["speed"])
        cost_in_cent = int(offer["monthlyCostInCent"])
        cost = cost_in_cent / 100
        duration = int(offer["durationInMonths"])
        after_two_years_cost_in_cent = int(offer["afterTwoYearsMonthlyCost"])
        after_two_years_cost = after_two_years_cost_in_cent / 100
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
        # if max_age is not None:
        #     age_text = f", for people under {max_age}"
        # else:
        #     age_text = ""
        # print(
        #     f" - {name}: {speed} Mbps for {cost:.2f} for the first {duration} months,", 
        #     f"{voucher_desc if voucher_desc else ''}", 
        #     f"{after_two_years_cost:.2f} after,",
        #     f"{'Unlimited' if unlimited else 'Capped'} data",
        #     age_text
        #     )
       
   

if __name__ == "__main__":
    main()