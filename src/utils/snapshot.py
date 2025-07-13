import os
import json

# --- Snapshot Management ---
# Create a directory to store snapshots if it doesn't exist
SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "snapshots")
# Ensure the snapshot directory exists
os.makedirs(SNAPSHOT_DIR, exist_ok=True)
# This directory is used to store snapshots of offers
def save_snapshot(snapshot_id, data):
    path = os.path.join(SNAPSHOT_DIR, f"{snapshot_id}.json")
    with open(path, "w") as f:
        json.dump(data, f)
# Load a snapshot by its ID
def load_snapshot(snapshot_id):
    path = os.path.join(SNAPSHOT_DIR, f"{snapshot_id}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)