# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)  # allow requests from the frontend

# Get API key from environment variable (recommended) or hardcode (NOT recommended)
API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")  # set this before running

if not API_KEY:
    print("Warning: OPENWEATHER_API_KEY is not set. Set it as an environment variable before running.")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def fetch_weather_by_params(params):
    """Call OpenWeatherMap and return parsed JSON or an error dict."""
    params['appid'] = API_KEY
    params['units'] = params.get('units', 'metric')
    try:
        resp = requests.get(BASE_URL, params=params, timeout=8)
    except requests.RequestException as e:
        return {"error": "Network error contacting weather service.", "details": str(e)}, 503

    try:
        data = resp.json()
    except ValueError:
        return {"error": "Invalid response from weather service."}, 502

    # Handle typical OWM error responses
    if resp.status_code == 401:
        return {"error": "Invalid API key. Check your OPENWEATHER_API_KEY."}, 401
    if resp.status_code == 404:
        return {"error": "Location not found."}, 404
    if resp.status_code != 200:
        # return message from API if available
        return {"error": data.get("message", "Weather service error."), "raw": data}, resp.status_code

    # Parse and return only the fields the frontend expects
    try:
        result = {
            "name": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "temp": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "humidity": data.get("main", {}).get("humidity"),
            "pressure": data.get("main", {}).get("pressure"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "description": data.get("weather", [{}])[0].get("description", "").title(),
            "icon": data.get("weather", [{}])[0].get("icon")
        }
        return result, 200
    except Exception as e:
        return {"error": "Failed to parse weather response.", "details": str(e)}, 500

@app.route('/weather')
def weather():
    """Accepts either ?city=CityName OR ?lat=...&lon=..."""
    if not API_KEY:
        return jsonify({"error": "Server missing OpenWeather API key (OPENWEATHER_API_KEY)."}), 500

    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    params = {}
    if city:
        params['q'] = city
    elif lat and lon:
        params['lat'] = lat
        params['lon'] = lon
    else:
        return jsonify({"error": "Provide ?city=CityName or ?lat=...&lon=..."}), 400

    data, status = fetch_weather_by_params(params)
    return jsonify(data), status

@app.route('/')
def root():
    # serve index.html (assumes file is in same folder)
    return send_from_directory('.', 'index.html')

# serve static assets too (if any)
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    # Flask dev server
    app.run(host='127.0.0.1', port=5000, debug=True)
