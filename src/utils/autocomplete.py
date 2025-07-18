import requests
import os
import json

NOMINATIM_URL = os.getenv("NOMINATIM_URL")
HEADERS = json.loads(os.getenv("HEADERS"))

def fetch_plz_suggestions(query):
    """
    Returns a list of German postal code suggestions based on the given query.
    Uses Nominatim's search API to find postal codes and cities that match the prefix.
    """
    # Ensure the query is a valid postal code prefix
    query = query.strip()
    if not query.isdigit():
        return []

    params = {
        "postalcode": query,         # structured field for postcodes
        "countrycodes": "de",        # hard filter to Germany
        "format": "json",            # JSON output
        "addressdetails": 1,         # include breakdown into components
        "limit": 10                  # max results
    }
    resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS)
    resp.raise_for_status()
    results = resp.json()

    seen = set()
    suggestions = []
    for result in results:
        addr = result.get("address", {})
        plz = addr.get("postcode")
        city = addr.get("municipality") or addr.get("city") or addr.get("town") or addr.get("village")
        if plz and city and plz.startswith(query):
            key = f"{plz} {city}"
            if key not in seen:
                seen.add(key)
                suggestions.append({
                  "display": key,
                  "postcode": plz,
                  "city": city
                })
                if len(suggestions) >= 10:
                    break
    return suggestions

def fetch_street_suggestions(query, city):
    """
    Returns street-name autocomplete suggestions in the given German city.
    Uses Nominatim's autocomplete mode for prefix searches.
    """
    params = {
        "street":         query,     # structured field for street name (no house number)
        "city":           city,      # structured city field
        "countrycodes":   "de",      # hard filter to Germany
        "format":         "json",    # JSON output
        "addressdetails": 1,         # include components
        "limit":          10         # max results
    }
    resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS)
    resp.raise_for_status()
    results = resp.json()

    seen = set()
    suggestions = []
    for r in results:
        addr = r.get("address", {})
        street = addr.get("road")
        if street and street not in seen:
            seen.add(street)
            suggestions.append({"display": street})
    return suggestions