from .weather_tool import get_weather
from .hotel_tool import search_hotels

# TOOLS = [
#     {
#         "name": "get_weather",
#         "description": "Get current weather of a city. Input: city name",
#         "func": get_weather
#     },
#     {
#         "name": "search_hotels",
#         "description": "Search hotels in a city",
#         "func": search_hotels
#     }
# ]


TOOLS = [
    {
        "name": "get_weather",
        "description": (
            "Lấy thông tin thời tiết. "
            "YÊU CẦU 2 THAM SỐ: "
            "1. city: Tên thành phố (str), "
            "2. target_date_str: Ngày định dạng YYYY-MM-DD (str). "
            "Ví dụ: get_weather('Ho Chi Minh', '2026-04-07')"
        ),
        "func": get_weather
    },
    {
        "name": "search_hotels",
        "description": (
            "Tìm kiếm khách sạn tại một địa điểm. "
            "YÊU CẦU 2 THAM SỐ: "
            "1. city: Tên thành phố (str), "
            "2. checkin_date: Ngày nhận phòng YYYY-MM-DD (str). "
            "Ví dụ: search_hotels('Ho Chi Minh', '2026-04-07')"
        ),
        "func": search_hotels
    }
]