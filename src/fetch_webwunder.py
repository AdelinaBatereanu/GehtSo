from dotenv import load_dotenv
import os
import requests
import pandas as pd
import io

load_dotenv()
api_key = os.getenv("WEBWUNDER_API_KEY")

def fetch_offers(api_key, installation, connection_enum, address):
    
    url = "https://webwunder.gendev7.check24.fun/endpunkte/soap/ws/getInternetOffers"

    envelope = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:gs="http://webwunder.gendev7.check24.fun/offerservice">
                    <soapenv:Header/>
                    <soapenv:Body>
                        <gs:legacyGetInternetOffers>
                            <gs:input>
                                <gs:installation>{str(installation).lower()}</gs:installation>
                                <gs:connectionEnum>{connection_enum}</gs:connectionEnum>
                                <gs:address>
                                <gs:street>{address['street']}</gs:street>
                                <gs:houseNumber>{address['houseNumber']}</gs:houseNumber>
                                <gs:city>{address['city']}</gs:city>
                                <gs:plz>{address['plz']}</gs:plz>
                                <gs:countryCode>{address['countryCode']}</gs:countryCode>
                                </gs:address>
                            </gs:input>
                        </gs:legacyGetInternetOffers>
                    </soapenv:Body>
                    </soapenv:Envelope>"""

    headers = {"X-Api-Key": api_key}

    response = requests.post(url, data=envelope, headers=headers)
    return response

if __name__ == "__main__":
    address = {
        "street": "Bendelstrasse",
        "houseNumber": "37",
        "city": "Aachen",
        "plz": "52062",
        "countryCode": "DE"
    }

    resp = fetch_offers(api_key, installation=False, connection_enum="DSL", address=address)

    print("HTTP status code:", resp.status_code)
    print("Response XML:\n", resp.text)
