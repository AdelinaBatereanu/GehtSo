import os
import json
import time
import hashlib
import pandas as pd

CACHE_DIR = 'cache'
CACHE_TIME = int(float(os.getenv("CACHE_TIME", "3600")))  # Default to 3600 seconds

# Create cache directory if it doesn't exist
def make_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

# Create a unique cache path based on provider name and address
def cache_path(provider_name, address):
    # Use a hash to avoid filesystem issues
    address_str = json.dumps(address, sort_keys=True)
    address_hash = hashlib.md5(address_str.encode()).hexdigest()
    filename = f"{provider_name}_{address_hash}.json"
    return os.path.join(CACHE_DIR, filename)

# Save data to cache with a timestamp
def save_to_cache(provider_name, address, data):
    make_cache_dir()
    # Convert DataFrame to list of dicts for JSON serialization
    if isinstance(data, pd.DataFrame):
        data = data.to_dict(orient="records")
    entry = {
        'timestamp': time.time(),
        'data': data
    }
    with open(cache_path(provider_name, address), 'w') as f:
        json.dump(entry, f)

# Load data from cache if it exists and is not expired
def load_from_cache(provider_name, address):
    path = cache_path(provider_name, address)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        entry = json.load(f)
    timestamp = entry.get('timestamp', 0)
    if time.time() - timestamp > CACHE_TIME:
        return None
    data = entry.get('data')
    # Convert list of dicts back to DataFrame
    if isinstance(data, list):
        try:
            import pandas as pd
            return pd.DataFrame(data)
        except ImportError:
            pass
    return data

# Retrieve provider data with caching
def get_provider_data(provider_name, address, fetch_func):
    """
    Try cache first, else call fetch_func(address), then cache it.
    """
    data = load_from_cache(provider_name, address)
    if data is not None:
        return data
    data = fetch_func(address)
    save_to_cache(provider_name, address, data)
    return data