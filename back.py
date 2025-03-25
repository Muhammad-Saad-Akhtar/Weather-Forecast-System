from fastapi import FastAPI, HTTPException
import requests
import os
from functools import lru_cache
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Load API key securely from environment variable
API_KEY = "0149336386bc4881934182637252503"
if not API_KEY:
    raise ValueError("Missing API key! Set the WEATHER_API_KEY environment variable.")

BASE_URL = "http://api.weatherapi.com/v1"

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@lru_cache(maxsize=100)
def fetch_weather(city: str):
    """Fetch current weather data from WeatherAPI.com with caching."""
    url = f"{BASE_URL}/current.json?key={API_KEY}&q={city}&aqi=no"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        raise HTTPException(status_code=401, detail="Invalid API key or unauthorized access.")
    elif response.status_code == 400:
        raise HTTPException(status_code=400, detail="Bad request. Check the city name.")
    elif response.status_code == 500:
        raise HTTPException(status_code=500, detail="WeatherAPI server error. Try again later.")
    else:
        raise HTTPException(status_code=response.status_code, detail="Unexpected error from WeatherAPI.")

@lru_cache(maxsize=100)
def fetch_forecast(city: str, days: int = 3):
    """Fetch 3-day weather forecast data from WeatherAPI.com with caching."""
    url = f"{BASE_URL}/forecast.json?key={API_KEY}&q={city}&days={days}&aqi=no&alerts=no"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch forecast data.")

@app.get("/weather")
def get_weather(city: str):
    """API endpoint to get current weather data for a given city."""
    try:
        data = fetch_weather(city)
        return {
            "city": data["location"]["name"],
            "country": data["location"]["country"],
            "temperature": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "wind_speed": data["current"]["wind_kph"],
            "humidity": data["current"]["humidity"],
            "feels_like": data["current"]["feelslike_c"],
            "uv_index": data["current"].get("uv", "N/A"),
            "visibility": data["current"].get("vis_km", "N/A"),
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/forecast")
def get_forecast(city: str):
    """API endpoint to get 3-day weather forecast for a given city."""
    try:
        data = fetch_forecast(city)
        forecast_days = [
            {
                "date": day["date"],
                "temperature_max": day["day"]["maxtemp_c"],
                "temperature_min": day["day"]["mintemp_c"],
                "condition": day["day"]["condition"]["text"],
                "wind_speed": day["day"]["maxwind_kph"],
                "humidity": day["day"]["avghumidity"],
            }
            for day in data["forecast"]["forecastday"]
        ]
        return {"city": data["location"]["name"], "country": data["location"]["country"], "forecast": forecast_days}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)