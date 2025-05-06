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

def main():
    response = requests.get(BASE_URL, params=params, headers=headers)
    print("Status code:", response.status_code) # 200 OK; 400 bad request; 401 autorisation failed; 500 server error
    text_stream = io.StringIO(response.text)
    reader = csv.DictReader(text_stream)
    for row in reader:
        print(row)

if __name__ == "__main__":
    main()