from dotenv import load_dotenv
import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np

load_dotenv()
API_KEY = os.getenv("WEBWUNDER_API_KEY")

BASE_URL = "https://webwunder.gendev7.check24.fun/endpunkte/soap/ws/getInternetOffers"

def fetch_offers(installation, connection_type, address):
    """
    Fetch offers from the WebWunder API for a given address
    Args:
        installation (bool)
        connection_type (str): "fiber", "dsl", "cable"
        address = {
            "street": str,
            "houseNumber": str,
            "city": str,
            "plz": str,
            "countryCode": str
        }
    Returns:
        response: Response object from the requests library
    """
    envelope = f"""<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:gs="http://webwunder.gendev7.check24.fun/offerservice">
                    <soapenv:Header/>
                    <soapenv:Body>
                        <gs:legacyGetInternetOffers>
                            <gs:input>
                                <gs:installation>{str(installation).lower()}</gs:installation>
                                <gs:connectionEnum>{connection_type.upper()}</gs:connectionEnum>
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

    headers = {"X-Api-Key": API_KEY}
    response = requests.post(BASE_URL, data=envelope, headers=headers)
    # print(response.text[:1000])  # Print the first 1000 characters of the response for debugging
    response.raise_for_status()
    return response

def parse_offers(response):
    """
    Parse the XML response from the WebWunder API and extracts relevant information
    Returns:
        pd.DataFrame with the following columns:
            provider, product_id, name, speed_mbps, cost_eur,
            min_order_value_eur, promo_price_eur, voucher_fixed_eur,
            voucher_percent, duration_months, after_two_years_eur,
            connection_type
    """
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
        product_id   = prod.find("ns2:productId", ns).text
        provider     = prod.find("ns2:providerName", ns).text

        info         = prod.find("ns2:productInfo", ns)
        speed_mbps   = int(info.find("ns2:speed", ns).text)
        cost_cent    = int(info.find("ns2:monthlyCostInCent", ns).text)
        post25_cent  = int(info.find("ns2:monthlyCostInCentFrom25thMonth", ns).text)

        voucher_info   = info.find("ns2:voucher", ns)
        voucher_type = voucher_info.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}type")
        # if voucher is a percentage
        if voucher_type == "ns2:percentageVoucher":
            voucher_percent = int(voucher_info.find("ns2:percentage", ns).text)
            voucher_fixed_cent = int(voucher_info.find("ns2:maxDiscountInCent", ns).text)
            # if voucher percent applied over voucher duration < max voucher value
            # voucher in percent is used to calculate the promo price
            if voucher_percent / 100 * cost_cent * 24 < voucher_fixed_cent:
                promo_price_cent = cost_cent - cost_cent * voucher_percent / 100
            # if voucher percent applied over voucher duration > max voucher value
            # max voucher value is used to calculate the promo price
            else:
                promo_price_cent = cost_cent - voucher_fixed_cent / 24
            min_cent = np.nan
        # if voucher is a fixed amount: discount price is calculated as
        # monthly cost - discount / 24 months
        else:
            voucher_fixed_cent = int(voucher_info.find("ns2:discountInCent", ns).text)
            voucher_percent = np.nan
            promo_price_cent = cost_cent - voucher_fixed_cent / 24
            min_cent = int(voucher_info.find("ns2:minOrderValueInCent", ns).text)
        duration = int(info.find("ns2:contractDurationInMonths", ns).text)
        connection_type = info.find("ns2:connectionType", ns).text

        offer = {
            "provider": "WebWunder",
            "product_id": product_id,
            "name": provider,
            "speed_mbps": speed_mbps,
            "cost_eur": cost_cent / 100,
            "min_order_value_eur": min_cent / 100,
            "promo_price_eur": promo_price_cent / 100,
            "voucher_fixed_eur": voucher_fixed_cent / 100,
            "voucher_percent": voucher_percent,
            "duration_months": duration,
            "after_two_years_eur": post25_cent / 100,
            "connection_type": connection_type.lower()  
        }

        parsed.append(offer)
    df = pd.DataFrame(parsed)
    return df

def get_offers(address_input):
    """
    Main function to fetch and transform offers from WebWunder API
    """
    address = {
        "street": address_input["street"],
        "houseNumber": address_input["house_number"],
        "city": address_input["city"],
        "plz": address_input["plz"],
        "countryCode": "DE"
    }

    all_offers = []
    # Fetch offers for all connection types and installation options
    print("Fetching offers for WebWunder")
    #TODO: make this async
    connection_types = ["fiber", "dsl", "cable"]
    for connection_type in connection_types:
        for installation in [True, False]:
            response = fetch_offers(installation, connection_type, address)
            offers = parse_offers(response)
            offers["installation_included"] = installation
            all_offers.append(offers)

    df = pd.concat(all_offers, ignore_index=True)
    print(f"Found {len(df)} offers, Webwunder")
    return df

if __name__ == "__main__":
    address = {
        "street": "Hauptstrasse",
        "house_number": "5A",
        "plz": "10115",
        "city": "Berlin"
    }
    df = get_offers(address)
    pd.set_option('display.max_columns', None)
    print(df.head(40))