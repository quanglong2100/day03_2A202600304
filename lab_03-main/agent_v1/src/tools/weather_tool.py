import requests
import os

WEATHER_API_KEY = "e2cbc53da1014aba85e52505260604"

def get_weather(city: str) -> str:
    """
    Get current weather for a city using WeatherAPI.com
    """
    try:
        url = "http://api.weatherapi.com/v1/current.json"
        params = {
            "key": WEATHER_API_KEY,
            "q": city,
            "aqi": "no"
        }

        response = requests.get(url, params=params)
        data = response.json()

        if "error" in data:
            return f"Weather API error: {data['error']['message']}"

        location = data["location"]["name"]
        temp = data["current"]["temp_c"]
        condition = data["current"]["condition"]["text"]

        return f"Weather in {location}: {temp}°C, {condition}"

    except Exception as e:
        return f"Weather API failed: {str(e)}"