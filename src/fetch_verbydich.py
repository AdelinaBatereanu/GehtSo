import requests 
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = "https://verbyndich.gendev7.check24.fun/check24/data/"
API_KEY = os.getenv("VERBYNDICH_API_KEY")

address = "Frauenstrasse;11;München;80469"
params = {
            "apiKey": API_KEY,
            "page": 0
        }

def fetch_verbyndich(address, params):
    response = requests.post(BASE_URL, params=params, data=address)
    print(response.status_code)
    return

fetch_verbyndich(address, params)