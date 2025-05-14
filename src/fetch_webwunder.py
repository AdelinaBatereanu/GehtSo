from dotenv import load_dotenv
import os
import requests
import pandas as pd
import io
import xml.etree.ElementTree as ET

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

def parse_offers(response):
    root = ET.fromstring(response.text)
    ns = {
    "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
    "ns2": "http://webwunder.gendev7.check24.fun/offerservice"
    }
    body = root.find("soapenv:Body", ns)
    output = body.find("Output")
    offers = output.findall("ns2:products", ns)
    parsed = []
    for prod in offers:
        # product_id   = prod.find("ns2:productId", ns).text
        provider     = prod.find("ns2:providerName", ns).text

        info         = prod.find("ns2:productInfo", ns)
        speed_mbps   = int(info.find("ns2:speed", ns).text)
        cost_cent    = int(info.find("ns2:monthlyCostInCent", ns).text)
        post25_cent  = int(info.find("ns2:monthlyCostInCentFrom25thMonth", ns).text)
# TODO: fix voucher
        voucher_el   = info.find("ns2:voucher", ns)
        voucher_type = voucher_el.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}type")
        discount_cent = int(voucher_el.find("ns2:discountInCent", ns).text)
        min_cent      = int(voucher_el.find("ns2:minOrderValueInCent", ns).text)

        duration     = int(info.find("ns2:contractDurationInMonths", ns).text)
        conn_type    = info.find("ns2:connectionType", ns).text

        cost_eur           = cost_cent / 100
        post_promo_eur     = post25_cent / 100
        voucher_desc       = f"{voucher_type}: €{discount_cent/100:.2f} off, min order €{min_cent/100:.2f}"

        offer = {
            "name": provider,
            "speed_mbps": speed_mbps,
            "cost_eur": cost_eur,
            "voucher": voucher_desc,
            "duration_months": duration,
            "post_promo_cost_eur": post_promo_eur,
            "connection_type": conn_type,
# TODO: fix installation
            # "installation_included": installation,    
        }

        parsed.append(offer)
    df = pd.DataFrame(parsed)
    pd.set_option('display.max_columns', None)
    print(df.head())
    return df
# TODO: add provider name to the dataframe

if __name__ == "__main__":
    address = {
        "street": "Bendelstrasse",
        "houseNumber": "37",
        "city": "Aachen",
        "plz": "52062",
        "countryCode": "DE"
    }
# TODO: fix umlauts
# TODO: get all possible offers (not only dsl) -> check what is easier: get all offers and then filter or only get 
#       the ones i need
    offers = fetch_offers(api_key, installation=False, connection_enum="DSL", address=address)
    parse_offers(offers)

    
