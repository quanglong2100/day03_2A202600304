import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional


RAPID_API_KEY = os.getenv("RAPID_API_KEY", "********")


class HotelSearchTool:
    """
    Hotel search tool using Booking.com RapidAPI
    Maps parameters from analyze_intent to RapidAPI query params
    """
    
    name = "search_hotels"
    description = """Tìm kiếm khách sạn theo location, date và budget.
Args:
  - city (str): Tên thành phố (e.g., "Ho Chi Minh", "Hanoi", "Da Nang", "Nha Trang")
  - date (str, optional): Ngày check-in format YYYY-MM-DD (từ analyze_intent)
  - budget_min (int, optional): Ngân sách tối thiểu VNĐ
  - budget_max (int, optional): Ngân sách tối đa VNĐ
  - limit (int, optional): Số lượng hotels cần trả về (default: 3)
Returns: JSON với danh sách hotels (name, address, rating, price)"""
    
    # City bounding boxes (latitude, longitude coordinates)
    CITY_BBOX = {
        "Ho Chi Minh": "10.7,10.9,106.6,106.8",
        "Hanoi": "20.8,21.3,105.6,106.1",
        "Hanoi": "21.0,21.1,105.8,105.9",
        "Da Nang": "16.0,16.1,108.1,108.3",
        "Nha Trang": "12.2,12.3,109.1,109.2",
        "Hoi An": "15.8,15.9,108.3,108.4",
        "Vung Tau": "10.3,10.4,107.0,107.1",
        "Phu Quoc": "10.1,10.3,103.9,104.1",
        "Dalat": "11.9,12.0,108.4,108.5"
    }
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or RAPID_API_KEY
        if not self.api_key or self.api_key == "********":
            print("⚠️  RAPID_API_KEY chưa được config. Sử dụng mock data.")
            self.use_mock = True
        else:
            self.use_mock = False
    
    def run(self, city: str, date: str = None, budget_min: int = None, 
            budget_max: int = None, limit: int = 3) -> str:
        """
        Search hotels với parameters từ analyze_intent.
        
        Args:
            city: Tên thành phố
            date: Ngày check-in (YYYY-MM-DD), nếu None thì dùng ngày mai
            budget_min: Ngân sách min (VNĐ)
            budget_max: Ngân sách max (VNĐ)
            limit: Số lượng hotels cần trả về
            
        Returns:
            JSON string với hotel list
        """
        print(f"🏨 Hotel search: {city}, date={date}, budget={budget_min}-{budget_max}, limit={limit}")
        
        if self.use_mock:
            return self._mock_hotel_search(city, date, budget_min, budget_max, limit)
        
        # Parse dates
        if date:
            try:
                arrival_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                return json.dumps({
                    "error": f"Invalid date format: {date}. Expected YYYY-MM-DD"
                }, ensure_ascii=False)
        else:
            # Default: tomorrow
            arrival_date = datetime.now().date() + timedelta(days=1)
        
        # Default checkout: 1 night after check-in
        departure_date = arrival_date + timedelta(days=1)
        
        # Get bbox for city
        bbox = self.CITY_BBOX.get(city, self.CITY_BBOX.get("Ho Chi Minh"))
        
        # Build RapidAPI query params
        querystring = {
            "arrival_date": arrival_date.isoformat(),      # từ analyze_intent date
            "departure_date": departure_date.isoformat(),  # date + 1 day
            "room_qty": "1",                               # default
            "guest_qty": "1",                              # default
            "bbox": bbox,                                  # từ location
            "search_id": "none",                           # deprecated
            "children_qty": "0",                           # default
            "languagecode": "en-us",                       # default
            "travel_purpose": "leisure",                   # default
            "order_by": "popularity",                      # hoặc "price" nếu có budget
            "offset": "0"                                  # first page
        }
        
        # Optional: filter by price if budget provided
        if budget_min or budget_max:
            querystring["order_by"] = "price"  # Sort by price khi có budget
        
        url = "https://apidojo-booking-v1.p.rapidapi.com/properties/list-by-map"
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "apidojo-booking-v1.p.rapidapi.com"
        }
        
        try:
            print(f"   → Calling RapidAPI: {url}")
            response = requests.get(url, headers=headers, params=querystring, timeout=15)
            data = response.json()
            
            if "error" in data:
                return json.dumps({
                    "error": data['error']
                }, ensure_ascii=False)
            
            # Parse response
            if "result" in data:
                hotels = data["result"]
            else:
                hotels = data.get("results", [])
            
            if not hotels:
                return json.dumps({
                    "location": city,
                    "message": "Không tìm thấy khách sạn phù hợp",
                    "hotels": []
                }, ensure_ascii=False, indent=2)
            
            # Process and filter hotels
            hotel_list = []
            for h in hotels[:20]:  # API returns max 20
                price = h.get("min_total_price", 0)
                
                # Convert price to VND if needed (giả sử API trả về USD)
                # 1 USD ≈ 24,000 VND (approximate)
                price_vnd = price * 24000 if price else 0
                
                # Filter by budget if provided
                if budget_min and price_vnd < budget_min:
                    continue
                if budget_max and price_vnd > budget_max:
                    continue
                
                hotel_info = {
                    "name": h.get("hotel_name", "Unknown"),
                    "address": h.get("address", "N/A"),
                    "rating": h.get("review_score", "N/A"),
                    "price_vnd": int(price_vnd) if price_vnd else "N/A",
                    "price_display": f"{int(price_vnd):,} VNĐ" if price_vnd else "N/A"
                }
                hotel_list.append(hotel_info)
                
                # Limit results
                if len(hotel_list) >= limit:
                    break
            
            result = {
                "location": city,
                "check_in": str(arrival_date),
                "check_out": str(departure_date),
                "total_found": len(hotel_list),
                "hotels": hotel_list
            }
            
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "message": "Lỗi khi gọi Hotel API"
            }, ensure_ascii=False)
    
# Wrapper function for backward compatibility
def search_hotels(city: str, date: str = None, budget_min: int = None,
                 budget_max: int = None, limit: int = 3) -> str:
    """
    Search hotels - wrapper function
    
    Args từ analyze_intent:
        city: location
        date: date
        budget_min: budget_min
        budget_max: budget_max
        limit: number_of_hotels
    """
    tool = HotelSearchTool()
    return tool.run(city, date, budget_min, budget_max, limit)