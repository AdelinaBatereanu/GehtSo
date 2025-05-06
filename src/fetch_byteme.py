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
    return list(reader)

def main():
    offers = fetch_offers()
    # for row in reader:
    #     name = row["providerName"]
    #     cost_in_cent = int(row["monthlyCostInCent"])
    #     cost = cost_in_cent / 100
    #     duration = int(row["durationInMonths"])
    #     print(f" - {name}: {cost:.2f} per month over {duration} months")

if __name__ == "__main__":
    main()