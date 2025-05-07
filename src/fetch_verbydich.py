import requests 
from dotenv import load_dotenv
import os

load_dotenv()
BASE_URL = "https://verbyndich.gendev7.check24.fun/check24/data"
API_KEY = os.getenv("VERBYNDICH_API_KEY")



# TODO: check for umlaut (encode utf-8)

def fetch_verbyndich():
    params = {
            "apiKey": API_KEY,
            "page": 0,
        }
    address = "Frauenstrasse;11;Munchen;80469"
    response = requests.post(BASE_URL, params=params, data=address, allow_redirects=False, timeout=10)  
    print(response.status_code)
    print(response.text[:500])
    return

# data = fetch_verbyndich(params)
# print(data[0])
fetch_verbyndich()