import unicodedata
from urllib.parse import quote_plus

def make_api_safe(string):
    normalized = unicodedata.normalize('NFKD', string)
    no_accents = normalized.encode('ascii', 'ignore').decode('ascii')
    return quote_plus(no_accents)