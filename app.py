from flask import Flask, jsonify, request
import requests
import time
import os

app = Flask(__name__)

cache = {}
CACHE_TIME = 60 * 60 * 12

@app.route("/weather")
def weather():
    city = request.args.get("city")

    if not city:
        return jsonify({"error": "city is required"}), 400

    city = city.strip().lower()

    if city in cache and time.time() - cache[city]["time"] < CACHE_TIME:
        return jsonify(cache[city]["data"])

    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1}
    )

    if geo.status_code != 200:
        return jsonify({"error": "Weather service unavailable"}), 503

    locations = geo.json().get("results")

    if not locations:
        return jsonify({"error": "City not found"}), 404

    location = locations[0]

    weather_response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m"
        }
    )

    if weather_response.status_code != 200:
        return jsonify({"error": "Weather service unavailable"}), 503

    data = {
        "city": location["name"],
        "country": location.get("country"),
        "weather": weather_response.json().get("current")
    }

    cache[city] = {
        "time": time.time(),
        "data": data
    }

    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5001, debug=True)