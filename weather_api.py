from flask import Flask, request, jsonify
import random
from datetime import datetime, timedelta

app = Flask(__name__)

def generate_weather_data(scale="local"):
    """Generate mock weather data based on scale"""
    base_temp = random.randint(15, 35)

    # Different data complexity based on scale
    if scale == "regional":
        return {
            "region": "Northeast US",
            "timestamp": datetime.now().isoformat(),
            "current_conditions": {
                "temperature": base_temp,
                "humidity": random.randint(30, 80),
                "conditions": random.choice(["sunny", "partly cloudy", "cloudy", "rainy"]),
                "wind_speed": random.randint(5, 25)
            },
            "forecast": [
                {
                    "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "high": base_temp + random.randint(-5, 10),
                    "low": base_temp - random.randint(5, 15),
                    "conditions": random.choice(["sunny", "partly cloudy", "cloudy", "rainy", "stormy"])
                } for i in range(1, 8)
            ],
            "alerts": random.choice([[], ["Heat Advisory in effect"], ["Thunderstorm Watch"]])
        }

    elif scale == "local":
        return {
            "city": "Boston",
            "state": "MA",
            "timestamp": datetime.now().isoformat(),
            "current_conditions": {
                "temperature": base_temp,
                "feels_like": base_temp + random.randint(-3, 5),
                "humidity": random.randint(40, 85),
                "conditions": random.choice(["sunny", "partly cloudy", "cloudy", "light rain", "heavy rain"]),
                "wind_speed": random.randint(3, 20),
                "wind_direction": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                "pressure": round(random.uniform(29.8, 30.3), 2),
                "visibility": random.randint(5, 15)
            },
            "forecast": [
                {
                    "date": (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                    "high": base_temp + random.randint(-3, 8),
                    "low": base_temp - random.randint(3, 12),
                    "conditions": random.choice(["sunny", "partly cloudy", "cloudy", "showers", "thunderstorms"]),
                    "precipitation_chance": random.randint(0, 100)
                } for i in range(1, 5)
            ],
            "air_quality": {
                "aqi": random.randint(20, 150),
                "category": random.choice(["Good", "Moderate", "Unhealthy for Sensitive Groups"])
            }
        }

    else:  # hyperlocal
        return {
            "location": "Newton Center, MA",
            "coordinates": {"lat": 42.3084, "lon": -71.1992},
            "timestamp": datetime.now().isoformat(),
            "current_conditions": {
                "temperature": base_temp,
                "feels_like": base_temp + random.randint(-2, 4),
                "humidity": random.randint(45, 90),
                "conditions": random.choice(["clear", "partly cloudy", "overcast", "light drizzle", "moderate rain"]),
                "wind_speed": random.randint(2, 18),
                "wind_direction": random.choice(["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]),
                "pressure": round(random.uniform(29.9, 30.2), 2),
                "visibility": random.randint(8, 15),
                "uv_index": random.randint(0, 11),
                "dew_point": base_temp - random.randint(5, 20)
            },
            "hourly_forecast": [
                {
                    "time": (datetime.now() + timedelta(hours=i)).strftime("%H:%M"),
                    "temperature": base_temp + random.randint(-5, 5),
                    "conditions": random.choice(["clear", "partly cloudy", "cloudy", "light rain"]),
                    "precipitation_chance": random.randint(0, 80),
                    "wind_speed": random.randint(1, 15)
                } for i in range(1, 13)
            ],
            "micro_climate": {
                "soil_temperature": base_temp - random.randint(2, 8),
                "grass_temperature": base_temp + random.randint(-3, 3),
                "local_precipitation_24h": round(random.uniform(0, 2.5), 2)
            },
            "nearby_conditions": [
                {
                    "location": "Chestnut Hill",
                    "distance_km": 2.1,
                    "temperature": base_temp + random.randint(-2, 2),
                    "conditions": random.choice(["clear", "cloudy", "light rain"])
                },
                {
                    "location": "Brookline",
                    "distance_km": 3.8,
                    "temperature": base_temp + random.randint(-3, 3),
                    "conditions": random.choice(["sunny", "overcast", "drizzle"])
                }
            ]
        }

@app.route('/api/v1/regional', methods=['GET'])
def regional_weather():
    """Regional weather endpoint"""
    return jsonify(generate_weather_data("regional"))

@app.route('/api/v1/local', methods=['GET'])
def local_weather():
    """Local weather endpoint"""
    return jsonify(generate_weather_data("local"))

@app.route('/api/v1/hyperlocal', methods=['GET'])
def hyperlocal_weather():
    """Hyperlocal weather endpoint"""
    return jsonify(generate_weather_data("hyperlocal"))

@app.route('/', methods=['GET'])
def home():
    """Root endpoint with API information"""
    return jsonify({
        "message": "Mock Weather API",
        "endpoints": {
            "/api/v1/regional": "Regional weather data",
            "/api/v1/local": "Local city weather data",
            "/api/v1/hyperlocal": "Hyperlocal neighborhood weather data"
        },
        "version": "1.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)