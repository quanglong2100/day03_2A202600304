import requests
from datetime import date, timedelta

RAPID_API_KEY = "21240fd7f4msh73024f18ed638e5p15ae4fjsnda1923fa4a1f"

def search_hotels(city: str = "Nha Trang", children_qty: int = 0):
    """
    Search hotels using Booking RapidAPI
    Returns list of top 5 hotels with name and review score.
    """

    # Set approximate bounding box for Nha Trang
    city_bbox = {
        "Nha Trang": "12.0,12.5,109.0,109.35",
        "Hanoi": "20.8,21.3,105.6,106.1",
        "Ho Chi Minh": "10.7,10.9,106.6,106.8"
    }

    arrival = date.today() + timedelta(days=1)
    departure = arrival + timedelta(days=3)

    url = "https://apidojo-booking-v1.p.rapidapi.com/properties/list-by-map"

    querystring = {
        "arrival_date": arrival.isoformat(),
        "departure_date": departure.isoformat(),
        "room_qty": "1",
        "guest_qty": "1",
        "bbox": city_bbox.get(city, "12.0,12.5,109.0,109.35"),
        "search_id": "none",
        "children_qty": str(children_qty),
        "languagecode": "en-us",
        "travel_purpose": "leisure",
        "order_by": "popularity",
        "offset": "0"
    }

    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "apidojo-booking-v1.p.rapidapi.com"
    }

    try:
        # Sửa lại đoạn này để debug
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()

        # In ra để kiểm tra các key thực tế có trong data
        print("Các keys trả về từ API:", data.keys()) 

        if "result" in data:
            hotels = data["result"]
            if not hotels:
                print("Cảnh báo: 'result' tìm thấy nhưng mảng bị rỗng. Kiểm tra lại bbox hoặc ngày tháng.")
        else:
            # Một số version dùng 'results' hoặc nằm trong 'data'
            hotels = data.get("results", [])

        hotel_list = []
        for h in hotels:
            hotel_info = {
                "name": h.get("hotel_name", "Unknown"),
                "score": h.get("review_score", "N/A"),
                "address": h.get("address", ""),
                "price": h.get("min_total_price", "N/A")
            }
            hotel_list.append(hotel_info)

        return {"hotels": hotel_list}

    except Exception as e:
        return {"error": str(e)}
