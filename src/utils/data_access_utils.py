import time
import logging
import pandas as pd

MAX_RETRIES = 3
RETRY_BACKOFF = 5  # seconds

def safe_get_offers(get_offers_func, address, provider_name):
    """
    Fetch offers with retry logic.
    Args:
        get_offers_func (function): Function to fetch offers.
        address (dict): Address to fetch offers for.
        provider_name (str): Name of the provider for logging.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return get_offers_func(address)
        except Exception as e:
            logging.error(f"[{provider_name}] Attempt {attempt} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF ** attempt)
            else:
                logging.error(f"[{provider_name}] All retries failed. Returning empty DataFrame.")
                return pd.DataFrame()