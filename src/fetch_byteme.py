import requests
import csv
import io
import dotenv

API_KEY = "placeholder_key"
BASE_URL = "https://api.byte-me.example.com/compare"
params = {
    "street":      "Hauptstraße",
    "houseNumber": "10",
    "city":        "Berlin",
    "plz":         "10115"
}

def main():
    print("Endpoint is:", BASE_URL)
    print(params)

if __name__ == "__main__":
    main()