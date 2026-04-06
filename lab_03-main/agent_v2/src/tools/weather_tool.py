import requests
import os
import json
from datetime import datetime, timedelta
from typing import Optional


WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "*******")


class WeatherTool:
    """
    Smart weather tool that automatically chooses between current and forecast API
    based on the requested date.
    """
    
    name = "get_weather"
    description = """Lấy thông tin thời tiết cho địa điểm và ngày cụ thể.
Tự động chọn API current (hôm nay) hoặc forecast (tương lai).
Args: 
  - city (str): Tên thành phố (e.g., "Ho Chi Minh", "Hanoi")
  - date (str, optional): Ngày cần xem thời tiết format YYYY-MM-DD. Nếu không có, lấy hôm nay.
Returns: Thông tin thời tiết chi tiết"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or WEATHER_API_KEY
        if not self.api_key or self.api_key == "*******":
            print("⚠️  WEATHER_API_KEY chưa được config. Sử dụng mock data.")
            self.use_mock = True
        else:
            self.use_mock = False
    
    def run(self, city: str, date: str = None) -> str:
        """
        Lấy thông tin thời tiết cho city và date.
        
        Args:
            city: Tên thành phố
            date: Ngày cần xem (YYYY-MM-DD). Nếu None, lấy hôm nay.
            
        Returns:
            JSON string hoặc text mô tả thời tiết
        """
        # Parse date nếu có
        today = datetime.now().date()
        target_date = today
        
        if date:
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                return json.dumps({
                    "error": f"Invalid date format: {date}. Expected YYYY-MM-DD"
                }, ensure_ascii=False)
        
        # So sánh với current date
        days_diff = (target_date - today).days
        
        print(f"🌤️  Weather request: {city}, {target_date} (diff: {days_diff} days)")
        
        # Chọn API phù hợp
        if days_diff < 0:
            # Past date - không support
            return json.dumps({
                "location": city,
                "date": str(target_date),
                "error": "Cannot get weather for past dates",
                "message": "Không thể lấy thời tiết cho ngày đã qua"
            }, ensure_ascii=False, indent=2)
        
        elif days_diff == 0:
            # Today - use current API
            print(f"   → Using CURRENT weather API")
            return self._get_current_weather(city)
        
        elif 1 <= days_diff <= 13:
            # Future (1-13 days) - use forecast API
            print(f"   → Using FORECAST weather API ({days_diff} days ahead)")
            return self._get_forecast_weather(city, days=days_diff)
        
        elif 14 <= days_diff <= 365:
            # Future (14-365 days) - use future weather (long-term forecast or climatology)
            print(f"   → Using FUTURE weather prediction ({days_diff} days ahead)")
            return self._get_future_weather(city, target_date)
        
        else:
            # Too far in future (>365 days)
            return json.dumps({
                "location": city,
                "date": str(target_date),
                "error": "Forecast only available for next 365 days",
                "message": f"API chỉ hỗ trợ dự báo 365 ngày. Ngày yêu cầu cách {days_diff} ngày."
            }, ensure_ascii=False, indent=2)
    
    def _get_current_weather(self, city: str) -> str:
        """Get current weather using WeatherAPI.com current endpoint"""
        
        if self.use_mock:
            return self._mock_current_weather(city)
        
        try:
            url = "http://api.weatherapi.com/v1/current.json"
            params = {
                "key": self.api_key,
                "q": city,
                "aqi": "no"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "error" in data:
                return json.dumps({
                    "error": data['error']['message']
                }, ensure_ascii=False)
            
            # Parse response
            result = {
                "location": data["location"]["name"],
                "country": data["location"]["country"],
                "date": data["location"]["localtime"].split()[0],
                "time": data["location"]["localtime"].split()[1],
                "temperature": {
                    "celsius": data["current"]["temp_c"],
                    "fahrenheit": data["current"]["temp_f"]
                },
                "condition": data["current"]["condition"]["text"],
                "humidity": data["current"]["humidity"],
                "wind_kph": data["current"]["wind_kph"],
                "feels_like_c": data["current"]["feelslike_c"],
                "description": f"Thời tiết hiện tại tại {data['location']['name']}: {data['current']['condition']['text']}, nhiệt độ {data['current']['temp_c']}°C, độ ẩm {data['current']['humidity']}%"
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "message": "Lỗi khi gọi Weather API"
            }, ensure_ascii=False)
    
    def _get_forecast_weather(self, city: str, days: int) -> str:
        """
        Get forecast weather for next 1-13 days using WeatherAPI.com forecast endpoint.
        
        Args:
            city: City name
            days: Number of days ahead (1-13)
        """
        
        if self.use_mock:
            target_date = datetime.now().date() + timedelta(days=days)
            return self._mock_forecast_weather(city, target_date)
        
        try:
            url = "http://api.weatherapi.com/v1/forecast.json"
            params = {
                "key": self.api_key,
                "q": city,
                "days": days + 1,  # API needs days+1 to include target day
                "aqi": "no"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "error" in data:
                return json.dumps({
                    "error": data['error']['message']
                }, ensure_ascii=False)
            
            # Get the last day in forecast (the target day)
            forecast_days = data["forecast"]["forecastday"]
            if len(forecast_days) <= days:
                return json.dumps({
                    "error": "Target date not in forecast range"
                }, ensure_ascii=False)
            
            forecast_day = forecast_days[days]  # Index by days (0=today, 1=tomorrow, etc)
            
            # Parse forecast
            result = {
                "location": data["location"]["name"],
                "country": data["location"]["country"],
                "date": forecast_day["date"],
                "temperature": {
                    "max_c": forecast_day["day"]["maxtemp_c"],
                    "min_c": forecast_day["day"]["mintemp_c"],
                    "avg_c": forecast_day["day"]["avgtemp_c"]
                },
                "condition": forecast_day["day"]["condition"]["text"],
                "humidity": forecast_day["day"]["avghumidity"],
                "chance_of_rain": forecast_day["day"]["daily_chance_of_rain"],
                "max_wind_kph": forecast_day["day"]["maxwind_kph"],
                "description": f"Dự báo thời tiết ngày {forecast_day['date']} tại {data['location']['name']}: {forecast_day['day']['condition']['text']}, nhiệt độ {forecast_day['day']['mintemp_c']}-{forecast_day['day']['maxtemp_c']}°C, độ ẩm {forecast_day['day']['avghumidity']}%, khả năng mưa {forecast_day['day']['daily_chance_of_rain']}%"
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "message": "Lỗi khi gọi Weather Forecast API"
            }, ensure_ascii=False)
    
    def _get_future_weather(self, city: str, target_date: datetime.date) -> str:
        """
        Get future weather prediction for 14-365 days ahead.
        Uses long-term forecast or climatology data.
        
        Note: Most free APIs only support up to 14 days. 
        For 14-365 days, we use climatology/historical averages.
        
        Args:
            city: City name
            target_date: Target date for prediction
        """
        
        if self.use_mock:
            return self._mock_forecast_weather(city, target_date)
        
        try:
            # Calculate days needed
            days_diff = (target_date - datetime.now().date()).days
            
            url = "http://api.weatherapi.com/v1/future.json"
            params = {
                "key": self.api_key,
                "q": city,
                "days": min(days_diff + 1, 14),  # API max 14 days
                "aqi": "no"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "error" in data:
                return json.dumps({
                    "error": data['error']['message']
                }, ensure_ascii=False)
            
            # Find the specific date in forecast
            target_date_str = str(target_date)
            forecast_day = None
            
            for day in data["forecast"]["forecastday"]:
                if day["date"] == target_date_str:
                    forecast_day = day
                    break
            
            if not forecast_day:
                return json.dumps({
                    "error": "Date not found in forecast",
                    "available_dates": [d["date"] for d in data["forecast"]["forecastday"]]
                }, ensure_ascii=False)
            
            # Parse forecast
            result = {
                "location": data["location"]["name"],
                "country": data["location"]["country"],
                "date": forecast_day["date"],
                "temperature": {
                    "max_c": forecast_day["day"]["maxtemp_c"],
                    "min_c": forecast_day["day"]["mintemp_c"],
                    "avg_c": forecast_day["day"]["avgtemp_c"]
                },
                "condition": forecast_day["day"]["condition"]["text"],
                "humidity": forecast_day["day"]["avghumidity"],
                "chance_of_rain": forecast_day["day"]["daily_chance_of_rain"],
                "max_wind_kph": forecast_day["day"]["maxwind_kph"],
                "description": f"Dự báo thời tiết ngày {forecast_day['date']} tại {data['location']['name']}: {forecast_day['day']['condition']['text']}, nhiệt độ {forecast_day['day']['mintemp_c']}-{forecast_day['day']['maxtemp_c']}°C, độ ẩm {forecast_day['day']['avghumidity']}%, khả năng mưa {forecast_day['day']['daily_chance_of_rain']}%"
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "message": "Lỗi khi gọi Weather Forecast API"
            }, ensure_ascii=False)
    
    def _mock_current_weather(self, city: str) -> str:
        """Mock current weather data"""
        return json.dumps({
            "location": city,
            "date": str(datetime.now().date()),
            "temperature": {"celsius": 28},
            "condition": "Sunny",
            "humidity": 70,
            "description": f"Thời tiết hiện tại tại {city}: Nắng, 28°C, độ ẩm 70%",
            "note": "MOCK DATA - API key chưa config"
        }, ensure_ascii=False, indent=2)
    
    def _mock_forecast_weather(self, city: str, target_date: datetime.date) -> str:
        """Mock forecast weather data"""
        return json.dumps({
            "location": city,
            "date": str(target_date),
            "temperature": {"max_c": 33, "min_c": 25, "avg_c": 29},
            "condition": "Partly cloudy",
            "humidity": 75,
            "chance_of_rain": 20,
            "description": f"Dự báo thời tiết ngày {target_date} tại {city}: Có mây, 25-33°C, độ ẩm 75%, khả năng mưa 20%",
            "note": "MOCK DATA - API key chưa config"
        }, ensure_ascii=False, indent=2)


# Wrapper function for backward compatibility
def get_weather(city: str, date: str = None) -> str:
    """
    Smart weather function that chooses between current and forecast API.
    
    Args:
        city: City name
        date: Optional date in YYYY-MM-DD format
        
    Returns:
        Weather information as JSON string
    """
    tool = WeatherTool()
    return tool.run(city, date)
