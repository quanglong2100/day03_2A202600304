import sys
import os

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

if root_path not in sys.path:
    sys.path.insert(0, root_path)
from src.core.ollama_provider import OllamaProvider
from src.agent.agent import ReActAgent
from src.tools import TOOLS

def main():
    llm = OllamaProvider(model_name="qwen2.5:7b")

    agent = ReActAgent(llm, TOOLS, max_steps=5)

    query = """Tôi muốn lập kế hoạch du lịch tại Hồ Chí Minh trong ngày 06/04/2026. 
        Hãy tư vấn:
        1. Dự báo thời tiết trong thời gian này.
        2. Gợi ý 3 khách sạn phù hợp với ngân sách 1.5 - 2 triệu VNĐ/đêm.
        3. Trả thông tin chi tiết: tên khách sạn, địa chỉ, điểm đánh giá, giá phòng dự kiến."""
    
    print("--- ĐANG XỬ LÝ ---")
    result = agent.run(query)
    
    print("\n===== KẾT QUẢ CUỐI CÙNG =====")
    print(result)

if __name__ == "__main__":
    main()