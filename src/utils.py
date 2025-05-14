import unicodedata
from urllib.parse import quote_plus

def make_api_safe(string):
    api_safe = unicodedata.normalize('NFKD', string)
    return api_safe.encode('ascii', 'ignore').decode('ascii')