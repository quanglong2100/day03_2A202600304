import json
import re
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class AnalyzeIntentTool:
    """
    Tool để phân tích ý định người dùng và trích xuất parameters cần thiết
    cho weather_tool và hotel_tool.
    
    Sử dụng LLM (local Phi-3 model) để parse thông tin từ query.
    """
    
    name = "analyze_intent"
    description = """Phân tích câu hỏi của người dùng về du lịch và trích xuất thông tin:
    - location (địa điểm)
    - date (ngày tháng)
    - budget_min, budget_max (ngân sách)
    - number_of_hotels (số lượng khách sạn cần gợi ý)
    Args: user_query (str)
    Returns: JSON string với các parameters đã trích xuất"""
    
    def __init__(self, llm_provider):
        """
        Args:
            llm_provider: LLM provider (local_provider recommended) để extract parameters
        """
        if llm_provider is None:
            raise ValueError("llm_provider is required for AnalyzeIntentTool")
        self.llm_provider = llm_provider
    
    def run(self, user_query: str) -> str:
        """
        Trích xuất intent và parameters từ user query sử dụng LLM.
        
        Args:
            user_query: Câu hỏi của người dùng
            
        Returns:
            JSON string chứa các parameters đã trích xuất
        """
        # Get current date for context
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        extraction_prompt = f"""Trích xuất thông tin từ câu hỏi du lịch sau và trả về ĐÚNG FORMAT JSON.

CONTEXT THỜI GIAN:
- Hôm nay: {today}
- Ngày mai: {tomorrow}

Câu hỏi: {user_query}

Hãy phân tích và trả về JSON với các trường sau:
- location: Tên thành phố (string, chuẩn hóa: "Thua Thien Hue", "Hanoi", "Ho Chi Minh", "Da Nang", "Nha Trang")
- date: Ngày du lịch format YYYY-MM-DD (string)
  * Nếu "ngày mai" → {tomorrow}
  * Nếu "hôm nay" → {today}
  * Nếu có DD/MM/YYYY → chuyển sang YYYY-MM-DD
  * Nếu không có → null
- budget_min: Ngân sách tối thiểu VNĐ (integer)
  * Nếu "<X triệu" → null (không có min)
  * Nếu "X-Y triệu" → X*1000000
  * Nếu không có → null
- budget_max: Ngân sách tối đa VNĐ (integer)
  * Nếu "<X triệu" → X*1000000
  * Nếu "X-Y triệu" → Y*1000000
  * Nếu "dưới X triệu" → X*1000000
  * Nếu không có → null
- number_of_hotels: Số khách sạn cần gợi ý (integer, mặc định 3)

CHUẨN HÓA ĐỊA ĐIỂM:
- "Huế" hoặc "Thừa Thiên Huế" → "Thua Thien Hue"
- "Hà Nội" → "Hanoi"
- "Hồ Chí Minh" hoặc "Sài Gòn" → "Ho Chi Minh"
- "Đà Nẵng" → "Da Nang"

CHUẨN HÓA NGÂN SÁCH:
- 1.5 triệu = 1500000
- 2 triệu = 2000000
- 3 triệu = 3000000

CHỈ TRẢ VỀ JSON, KHÔNG GIẢI THÍCH.

Ví dụ:
{{
  "location": "Thua Thien Hue",
  "date": "{tomorrow}",
  "budget_min": null,
  "budget_max": 3000000,
  "number_of_hotels": 3
}}

JSON:"""
        
        try:
            print(f"🔍 Analyzing intent with LLM...")
            response = self.llm_provider.generate(extraction_prompt)
            
            # Handle response from LLM
            if isinstance(response, dict):
                if 'text' in response:
                    response_text = response['text']
                elif 'content' in response:
                    response_text = response['content']
                else:
                    response_text = str(response)
            else:
                response_text = str(response)
            
            print(f"📤 LLM Response:\n{response_text[:200]}...")
            
            json_patterns = [
                r'```json\s*(\{.*?\})\s*```',  # JSON in markdown code block
                r'```\s*(\{.*?\})\s*```',       # JSON in plain code block
                r'(\{[^{}]*\{[^{}]*\}[^{}]*\})', # Nested JSON
                r'(\{.*?\})'                     # Simple JSON
            ]
            
            json_str = None
            for pattern in json_patterns:
                match = re.search(pattern, response_text, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    break
            
            if json_str:
                json_str = json_str.strip()
                
                parsed = json.loads(json_str)
                
                result = {
                    "location": parsed.get("location"),
                    "date": parsed.get("date"),
                    "budget_min": parsed.get("budget_min"),
                    "budget_max": parsed.get("budget_max"),
                    "number_of_hotels": parsed.get("number_of_hotels", 3)
                }
                
                print(f"✅ Extracted parameters successfully")
                return json.dumps(result, ensure_ascii=False, indent=2)
            else:
                raise ValueError("Could not find valid JSON in LLM response")
                
        except Exception as e:
            error_msg = f"❌ LLM extraction failed: {str(e)}"
            print(error_msg)
            
            # Return default values instead of failing completely
            default_result = {
                "location": None,
                "date": None,
                "budget_min": None,
                "budget_max": None,
                "number_of_hotels": 3,
                "error": str(e)
            }
            return json.dumps(default_result, ensure_ascii=False, indent=2)
     