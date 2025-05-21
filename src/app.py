from flask import Flask, request, jsonify, render_template
import compare_offers
from urllib.parse import urlencode
import pandas as pd
import numpy as np

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
    sort = request.args.get('sort', default="cost_first_years")
    speed = request.args.get('speed', default=None, type=int)
    # cost = request.args.get('cost', default=None, type=float)
    duration = request.args.get('duration', default=None, type=int)
    tv_required = request.args.get('tv', default=None)
    limit = request.args.get('limit', default=None, type=int)
    installation_required = request.args.get('installation', default=None)
    connection_types = request.args.get('connection_types', default=None, type=lambda x: x.split(","))
    providers = request.args.get('providers', default=None, type=lambda x: x.split(","))

    params = {
        "sort": sort,
        "speed": speed,
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

    df = compare_offers.get_all_offers()

    if speed:
        df = compare_offers.filter_speed(df, speed)
    # if cost:
    #     df = compare_offers.filter_cost(df, cost)
    if duration:
        df = compare_offers.filter_duration(df, duration)
    if tv_required:
        df = compare_offers.filter_tv(df, str2bool(tv_required))
    if limit:
        df = compare_offers.filter_limit(df, limit)
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

    return jsonify(df.to_dict(orient="records"))

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

#TODO: change np.nan and pd.NA to None (everywhere)