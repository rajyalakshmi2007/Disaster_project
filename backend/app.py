
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Disaster Alert Dashboard</title>

    <link rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">

    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background: #f0f4f8;
        }

        header {
            background: #b71c1c;
            color: white;
            padding: 20px;
            text-align: center;
        }

        .container {
            padding: 20px;
        }

        .card {
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 8px #cccccc;
        }

        select, input, button {
            padding: 10px;
            margin: 5px;
            font-size: 15px;
        }

        button {
            background: #1565c0;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        button:hover {
            background: #0d47a1;
        }

        #map {
            height: 400px;
            width: 100%;
            border-radius: 10px;
        }

        #alertBox {
            padding: 15px;
            border-radius: 8px;
            background: #e8f5e9;
            color: #1b5e20;
            font-weight: bold;
            white-space: pre-line;
        }

        footer {
            text-align: center;
            padding: 15px;
        }
    </style>
</head>

<body>

<header>
    <h1>🚨 Disaster Alert & Prediction System</h1>
    <p>AI-Based Multi-Disaster Monitoring Dashboard</p>
</header>

<div class="container">

    <div class="card">
        <h2>📍 Location Details</h2>

        <input type="text" id="location"
               placeholder="Enter location (e.g. Hyderabad)">

        <button onclick="searchLocation()">Search Location</button>

        <button onclick="getCurrentLocation()">
            Detect My Current Location
        </button>

        <p id="locationStatus">Location not detected yet.</p>
    </div>

    <div class="card">
        <h2>🌍 Disaster Monitoring Map</h2>
        <div id="map"></div>
    </div>

    <div class="card">
        <h2>⚠️ Disaster Risk Assessment</h2>

        <label>Select Disaster:</label>

        <select id="disaster">
            <option value="Flood">Flood</option>
            <option value="Cyclone">Cyclone</option>
            <option value="Earthquake">Earthquake</option>
            <option value="Landslide">Landslide</option>
            <option value="Heatwave">Heatwave</option>
            <option value="Wildfire">Wildfire</option>
        </select>

        <button onclick="assessDisaster()">Check Risk</button>

        <div id="alertBox">
            Select a disaster and check the risk.
        </div>
    </div>

    <div class="card">
        <h2>🌦️ Weather Information</h2>
        <p id="weather">Weather information will appear here.</p>
        <button onclick="getWeather()">Check Weather</button>
    </div>

</div>

<footer>
    Disaster Alert System | Final Year Project
</footer>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>
    let latitude = 17.3850;
    let longitude = 78.4867;

    let map = L.map('map').setView([latitude, longitude], 6);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'OpenStreetMap'
    }).addTo(map);

    let marker = L.marker([latitude, longitude])
        .addTo(map)
        .bindPopup("Default Location: Hyderabad")
        .openPopup();

    function updateMap(lat, lon, name) {
        latitude = lat;
        longitude = lon;

        map.setView([lat, lon], 10);

        marker.setLatLng([lat, lon])
              .bindPopup(name)
              .openPopup();

        document.getElementById("locationStatus").innerText =
            "Location: " + name +
            "\\nLatitude: " + lat +
            "\\nLongitude: " + lon;
    }

    function getCurrentLocation() {
        if (!navigator.geolocation) {
            alert("Your browser does not support location.");
            return;
        }

        navigator.geolocation.getCurrentPosition(
            function(position) {
                updateMap(
                    position.coords.latitude,
                    position.coords.longitude,
                    "Your Current Location"
                );

                getWeather();
            },
            function(error) {
                alert("Location permission denied or unavailable.");
            }
        );
    }

    async function searchLocation() {
        let place = document.getElementById("location").value;

        if (!place) {
            alert("Please enter a location.");
            return;
        }

        try {
            let response = await fetch(
                "https://nominatim.openstreetmap.org/search?format=json&q="
                + encodeURIComponent(place)
            );

            let data = await response.json();

            if (data.length === 0) {
                alert("Location not found.");
                return;
            }

            updateMap(
                parseFloat(data[0].lat),
                parseFloat(data[0].lon),
                place
            );

            getWeather();

        } catch (error) {
            alert("Unable to search location.");
        }
    }

    async function getWeather() {
        document.getElementById("weather").innerText =
            "Loading weather information...";

        try {
            let url =
                "https://api.open-meteo.com/v1/forecast"
                + "?latitude=" + latitude
                + "&longitude=" + longitude
                + "&current=temperature_2m,relative_humidity_2m,"
                + "precipitation,wind_speed_10m";

            let response = await fetch(url);
            let data = await response.json();

            let weather = data.current;

            document.getElementById("weather").innerText =
                "Temperature: " + weather.temperature_2m + " °C\\n" +
                "Humidity: " + weather.relative_humidity_2m + "%\\n" +
                "Precipitation: " + weather.precipitation + " mm\\n" +
                "Wind Speed: " + weather.wind_speed_10m + " km/h";

        } catch (error) {
            document.getElementById("weather").innerText =
                "Weather information unavailable.";
        }
    }

    async function assessDisaster() {
        let disaster = document.getElementById("disaster").value;

        let box = document.getElementById("alertBox");

        box.innerText = "Checking disaster risk...";

        try {
            let response = await fetch("/assess", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    disaster: disaster,
                    latitude: latitude,
                    longitude: longitude
                })
            });

            let result = await response.json();

            box.innerText =
                "Disaster: " + result.disaster + "\\n" +
                "Risk Level: " + result.risk + "\\n\\n" +
                result.english + "\\n\\n" +
                result.telugu;

            box.style.background =
                result.risk === "HIGH" ? "#ffcdd2" :
                result.risk === "MEDIUM" ? "#fff9c4" :
                "#e8f5e9";

            box.style.color =
                result.risk === "HIGH" ? "#b71c1c" :
                result.risk === "MEDIUM" ? "#795548" :
                "#1b5e20";

        } catch (error) {
            box.innerText = "Unable to assess disaster risk.";
        }
    }

    getWeather();
</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGE)


@app.route("/assess", methods=["POST"])
def assess():
    data = request.get_json()

    disaster = data.get("disaster", "Flood")

    # Demo risk assessment.
    # This is not a trained AI prediction model.
    risk_levels = {
        "Flood": "MEDIUM",
        "Cyclone": "LOW",
        "Earthquake": "LOW",
        "Landslide": "LOW",
        "Heatwave": "MEDIUM",
        "Wildfire": "LOW"
    }

    risk = risk_levels.get(disaster, "LOW")

    messages = {
        "LOW": (
            "No immediate warning in this demo. Stay informed.",
            "ఈ డెమోలో ప్రస్తుతం తక్కువ ప్రమాద స్థాయి ఉంది."
        ),
        "MEDIUM": (
            "Moderate risk in this demo. Please stay alert.",
            "మధ్యస్థ ప్రమాద స్థాయి. అప్రమత్తంగా ఉండండి."
        ),
        "HIGH": (
            "High risk! Follow official emergency instructions.",
            "అధిక ప్రమాదం! అధికారిక అత్యవసర సూచనలను పాటించండి."
        )
    }

    english, telugu = messages[risk]

    return jsonify({
        "disaster": disaster,
        "risk": risk,
        "english": english,
        "telugu": telugu
    })


if __name__ == "__main__":
    app.run(debug=True)
