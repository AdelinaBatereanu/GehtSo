import unicodedata
from urllib.parse import quote_plus

# Encode a string to be safe for API usage
def make_api_safe(string):
    string = string.replace("ß", "ss")
    normalized = unicodedata.normalize('NFKD', string)
    no_accents = normalized.encode('ascii', 'ignore').decode('ascii')
    return quote_plus(no_accents)

# Convert a string to a boolean value
def str2bool(value):
    return str(value).lower() in ["true", "1", "yes", "y"]