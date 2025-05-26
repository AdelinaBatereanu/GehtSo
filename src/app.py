from flask import Flask, request, jsonify, render_template, Response, stream_with_context, url_for, abort, render_template
import compare_offers
from urllib.parse import urlencode
import pandas as pd
import numpy as np
from utils import make_api_safe
import json
import asyncio
from uuid import uuid4

app = Flask(__name__)

def str2bool(value):
    return str(value).lower() in ["true", "1"]

def make_share_url(base, params):
    """
    base: str (base URL)
    params: dict (query parameters)
    """
    query_string = urlencode(params)
    return f"{base}?{query_string}"

@app.route("/offers")
def get_offers():
    # --- Require and sanitize address fields ---
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

    sort = request.args.get('sort', default="cost_first_years")
    speed = request.args.get('speed', default=None, type=int)
    age = request.args.get('age', default=None, type=int)
    # cost = request.args.get('cost', default=None, type=float)
    duration = request.args.get('duration', default=None, type=int)
    tv_required = request.args.get('tv', default=None)
    limit = request.args.get('limit', default=None)
    installation_required = request.args.get('installation', default=None)
    connection_types = request.args.get('connection_types', default=None, type=lambda x: x.split(","))
    providers = request.args.get('providers', default=None, type=lambda x: x.split(","))

    params = {
        "sort": sort,
        "speed": speed,
        "age": age,
        # "cost": cost,
        "duration": duration,
        "tv_required": tv_required,
        "limit": limit,
        "installation_required": installation_required,
        "connection_types": connection_types,
        "providers": providers
    }
    params = {key: value for key, value in params.items() if value is not None}
    share_url = make_share_url(request.host_url, params)
    print(f"Share URL: {share_url}")
    
    async def generate_async():
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, compare_offers.safe_get_offers, compare_offers.get_byteme_offers, address, "ByteMe"),
            loop.run_in_executor(None, compare_offers.safe_get_offers, compare_offers.get_pingperfect_offers, address, "Ping Perfect"),
            loop.run_in_executor(None, compare_offers.safe_get_offers, compare_offers.get_servusspeed_offers, address, "Servus Speed"),
            loop.run_in_executor(None, compare_offers.safe_get_offers, compare_offers.get_verbyndich_offers, address, "Verbyndich"),
            loop.run_in_executor(None, compare_offers.safe_get_offers, compare_offers.get_webwunder_offers, address, "WebWunder"),
        ]
        for coro in asyncio.as_completed(tasks):
            df = await coro

            # --- Handle missing values for this provider ---
            df = compare_offers.fill_columns(df)
        
            if speed:
                df = compare_offers.filter_speed(df, speed)
            if age:
                df = compare_offers.filter_age(df, age)
            # if cost:
            #     df = compare_offers.filter_cost(df, cost)
            if duration:
                df = compare_offers.filter_duration(df, duration)
            if tv_required:
                df = compare_offers.filter_tv(df, str2bool(tv_required))
            if limit == "none":
                df = compare_offers.filter_limit(df, "none")
            elif limit:
                df = compare_offers.filter_limit(df, int(limit))
            if installation_required:
                df = compare_offers.filter_installation(df, str2bool(installation_required))
            if connection_types is not None:
                df = compare_offers.filter_connection_types(df, connection_types)
            if providers:
                df = compare_offers.filter_provider(df, providers)

            if sort == "cost_first_years":
                df = compare_offers.sort_by_first_years_cost(df)
            elif sort == "cost_later_years":
                df = compare_offers.sort_by_after_two_years_cost(df)
            elif sort == "speed":
                df = compare_offers.sort_by_speed(df)

            for offer in df.to_dict(orient="records"):
                yield json.dumps(offer) + '\n'

    def generate():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        agen = generate_async()  # This is an async generator, not a coroutine!
        try:
            while True:
                chunk = loop.run_until_complete(agen.__anext__())
                yield chunk
        except StopAsyncIteration:
            pass

    return Response(stream_with_context(generate()), mimetype='application/x-ndjson')

@app.route("/")
def index():
    return render_template("index.html")

snapshots = {}

@app.route("/share", methods=["POST"])
def create_share():
    payload = request.get_json()
    offers = payload.get('offers')
    filters = payload.get('filters', {})
    if not offers:
        return jsonify({'error': 'No offers provided'}), 400
    snapshot_id = str(uuid4())
    snapshots[snapshot_id] = {"offers": offers, "filters": filters}
    share_url = url_for('view_share', snapshot_id=snapshot_id, _external=True)
    return jsonify({'share_url': share_url}), 201

@app.route("/share/<snapshot_id>")
def view_share(snapshot_id):
    snapshot = snapshots.get(snapshot_id)
    if not snapshot:
        return abort(404, description="Page not found")
    offers = snapshot.get("offers", [])
    filters = snapshot.get("filters", {})
    return render_template("index.html", offers=offers, filters=filters, snapshot_id=snapshot_id)

if __name__ == "__main__":
    app.run(debug=True)

#TODO: change np.nan and pd.NA to None (everywhere)