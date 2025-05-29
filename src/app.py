from flask import Flask, request, jsonify, render_template, Response, stream_with_context, url_for, abort, render_template, send_from_directory
import json
import asyncio
from uuid import uuid4

from utils import make_api_safe, fetch_plz_suggestions, fetch_street_suggestions, validate_address
import compare_offers

app = Flask(__name__)

"""Endpoint to get internet offers based on address"""
@app.route("/offers")
def get_offers():
    # --- Require address fields ---
    street = request.args.get('street', default=None)
    house_number = request.args.get('house_number', default=None)
    plz = request.args.get('plz', default=None)
    city = request.args.get('city', default=None)

    # Check all fields are present
    if not all([street, house_number, plz, city]):
        return jsonify({"error": "All address fields (street, house_number, plz, city) are required."}), 400

    # Sanitize each field
    address = {
        "street": make_api_safe(street),
        "house_number": make_api_safe(house_number),
        "plz": make_api_safe(plz),
        "city": make_api_safe(city)
    }

     # Validate address
    if not validate_address(street, house_number, plz, city):
        return jsonify({"error": "Invalid address."}), 400

    async def generate_async():
        """Asynchronous generator to fetch and yield offers."""
        # Create a new event loop for the async generator
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, compare_offers.safe_get_offers, compare_offers.get_byteme_offers, address, "ByteMe"),
            loop.run_in_executor(None, compare_offers.safe_get_offers, compare_offers.get_pingperfect_offers, address, "Ping Perfect"),
            loop.run_in_executor(None, compare_offers.safe_get_offers, compare_offers.get_servusspeed_offers, address, "Servus Speed"),
            loop.run_in_executor(None, compare_offers.safe_get_offers, compare_offers.get_verbyndich_offers, address, "VerbynDich"),
            loop.run_in_executor(None, compare_offers.safe_get_offers, compare_offers.get_webwunder_offers, address, "WebWunder"),
        ]
        # for each provider, create a task to fetch offers
        for coro in asyncio.as_completed(tasks):
            df = await coro

            # --- Handle missing values for this provider ---
            df = compare_offers.fill_columns(df)

            # --- Convert DataFrame to JSON and yield each offer ---
            for offer in df.to_dict(orient="records"):
                yield json.dumps(offer) + '\n'

    def generate():
        """Generator to stream offers as NDJSON."""
        # Create a new event loop for the async generator
        loop = asyncio.new_event_loop()
        # Set the new loop as the current event loop
        asyncio.set_event_loop(loop)
        # Create an async generator
        agen = generate_async()
        # Use the event loop to run the async generator and yield chunks
        # until StopAsyncIteration is raised
        try:
            while True:
                chunk = loop.run_until_complete(agen.__anext__())
                yield chunk
        except StopAsyncIteration:
            pass

    # --- Stream the offers as NDJSON ---
    return Response(stream_with_context(generate()), mimetype='application/x-ndjson')

"""Endpoint to render the main page"""
@app.route("/")
def index():
    return render_template("index.html")

# Dictionary to store snapshots of offers for sharing
snapshots = {}

"""Endpoint to create a shareable link for offers"""
@app.route("/share", methods=["POST"])
def create_share():
    payload = request.get_json()
    offers = payload.get('offers')
    filters = payload.get('filters', {})
    if not offers:
        return jsonify({'error': 'No offers provided'}), 400
    snapshot_id = str(uuid4())
    # Store the offers and filters in the snapshots dictionary
    snapshots[snapshot_id] = {"offers": offers, "filters": filters}
    # Generate a shareable URL for the snapshot
    share_url = url_for('view_share', snapshot_id=snapshot_id, _external=True)
    return jsonify({'share_url': share_url}), 201

"""Endpoint to view shared offers"""
@app.route("/share/<snapshot_id>")
def view_share(snapshot_id):
    snapshot = snapshots.get(snapshot_id)
    if not snapshot:
        return abort(404, description="Page not found")
    # Render the offers and filters from the snapshot
    offers = snapshot.get("offers", [])
    filters = snapshot.get("filters", {})
    return render_template("index.html", offers=offers, filters=filters, snapshot_id=snapshot_id)

"""Endpoint to autocomplete postal codes and street names"""
@app.route("/autocomplete")
def autocomplete_api():
    # --- Validate query parameters ---
    q = request.args.get("q", "").strip()
    field = request.args.get("field", "")
    if not q or field not in ("plz", "street"):
        return jsonify([]), 400
    # --- Fetch suggestions based on the field ---
    if field == "plz":
        suggestions = fetch_plz_suggestions(q)
    else:  # field == "street"
        city = request.args.get("city", "").strip()
        if not city:
            return jsonify([]), 400
        suggestions = fetch_street_suggestions(q, city)

    return jsonify(suggestions)

if __name__ == "__main__":
    # Run the Flask app
    app.run(debug=True)
