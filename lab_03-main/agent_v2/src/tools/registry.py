"""
Tool Registry - Đăng ký tất cả tools available cho ReAct Agent
"""

import os
from src.tools.analyze_intent_tool import AnalyzeIntentTool
from src.tools.weather_tool import get_weather
from src.tools.hotel_tool import search_hotels
from src.core.local_provider import LocalProvider


def get_available_tools():
    """
    Trả về danh sách tất cả tools có sẵn cho Agent.
    
    analyze_intent_tool sử dụng local_provider (Phi-3) riêng biệt
    để tiết kiệm chi phí và tốc độ.
    
    Returns:
        List[Dict]: Danh sách tools với format:
            - name: Tên tool
            - description: Mô tả chức năng
            - function: Callable function
    """
    
    # Khởi tạo local LLM provider cho analyze_intent
    model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
    print(f"🔧 Initializing local LLM for intent analysis: {model_path}")
    
    intent_llm = LocalProvider(model_path=model_path, n_ctx=2048)  # Smaller context for intent
    intent_tool = AnalyzeIntentTool(llm_provider=intent_llm)
    
    # 2. Weather Tool
    weather_tool_config = {
        "name": "get_weather",
        "description": """Lấy thông tin thời tiết cho địa điểm và ngày cụ thể.
Tự động chọn API current (hôm nay) hoặc forecast (tương lai dựa trên date).
Args: 
  - city (str): Tên thành phố (e.g., "Ho Chi Minh", "Hanoi", "Da Nang")
  - date (str, optional): Ngày cần xem thời tiết format YYYY-MM-DD (e.g., "2026-04-06"). Nếu không có, lấy hôm nay.
Returns: JSON string với thông tin thời tiết chi tiết (temperature, humidity, condition, description)""",
        "function": get_weather
    }
    
    # 3. Hotel Search Tool
    hotel_tool_config = {
        "name": "search_hotels",
        "description": """Tìm kiếm khách sạn theo location, date và budget.
Args:
  - city (str): Tên thành phố từ analyze_intent location
  - date (str, optional): Ngày check-in từ analyze_intent date (YYYY-MM-DD)
  - budget_min (int, optional): Ngân sách min từ analyze_intent budget_min (VNĐ)
  - budget_max (int, optional): Ngân sách max từ analyze_intent budget_max (VNĐ)
  - limit (int, optional): Số hotels từ analyze_intent number_of_hotels (default: 3)
Returns: JSON với hotels list (name, address, rating, price_vnd)""",
        "function": search_hotels
    }
    
    # 4. Analyze Intent Tool
    intent_tool_config = {
        "name": "analyze_intent",
        "description": """Phân tích câu hỏi của người dùng về du lịch và trích xuất thông tin:
    - location (địa điểm)
    - date (ngày tháng)
    - budget_min, budget_max (ngân sách)
    - number_of_hotels (số lượng khách sạn cần gợi ý)
    Args: user_query (str)
    Returns: JSON string với các parameters đã trích xuất""",
        "function": intent_tool.run
    }
    
    return [
        intent_tool_config,
        weather_tool_config,
        hotel_tool_config
    ]


def get_tool_by_name(tool_name: str, tools: list) -> dict:
    """
    Tìm tool theo tên.
    
    Args:
        tool_name: Tên tool cần tìm
        tools: Danh sách tools từ get_available_tools()
        
    Returns:
        Tool config dict hoặc None nếu không tìm thấy
    """
    for tool in tools:
        if tool["name"] == tool_name:
            return tool
    return None
