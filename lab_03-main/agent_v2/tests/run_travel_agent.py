"""
Run Travel Agent - Demo ReAct Agent với travel planning use case

Flow hoạt động:
1. Agent nhận query từ user
2. Sử dụng analyze_intent để trích xuất parameters
3. Dựa vào parameters, gọi get_weather và search_hotels
4. Tổng hợp kết quả và trả về Final Answer
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.core.local_provider import LocalProvider
from src.agent.agent import ReActAgent
from src.tools.registry import get_available_tools

# Load environment variables
load_dotenv()


def get_llm_provider(provider_name: str = None):
    """
    Khởi tạo LLM provider theo config.
    
    Args:
        provider_name: "openai" | "gemini" | "local"
        
    Returns:
        LLMProvider instance
    """
    if provider_name is None:
        provider_name = os.getenv("DEFAULT_PROVIDER", "local")
    
    print(f"🤖 Đang khởi tạo LLM Provider: {provider_name}")
    
    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY không được cấu hình trong .env")
        return OpenAIProvider(
            model_name=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
            api_key=api_key
        )
    
    elif provider_name == "gemini" or provider_name == "google":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY không được cấu hình trong .env")
        return GeminiProvider(
            model_name=os.getenv("DEFAULT_MODEL", "gemini-1.5-flash"),
            api_key=api_key
        )
    
    elif provider_name == "local":
        model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file không tìm thấy: {model_path}")
        print(f"📦 Đang load model: {model_path}")
        return LocalProvider(model_path=model_path, n_ctx=4096)
    
    else:
        raise ValueError(f"Provider không hợp lệ: {provider_name}")


def main():
    """Main execution function"""
    
    print("=" * 70)
    print("🌍 TRAVEL PLANNING AGENT - ReAct Implementation")
    print("=" * 70)
    
    try:
        # 1. Khởi tạo LLM Provider
        llm = get_llm_provider()
        print(f"✅ LLM Provider đã sẵn sàng: {llm.model_name}\n")
        
        # 2. Lấy danh sách tools
        # analyze_intent_tool sẽ tự động khởi tạo local_provider riêng
        tools = get_available_tools()
        print(f"🛠️  Đã load {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool['name']}: {tool['description'][:60]}...")
        print()
        
        # 3. Khởi tạo ReAct Agent
        agent = ReActAgent(
            llm=llm,
            tools=tools,
            max_steps=10  # Tăng lên 10 steps cho phép agent suy nghĩ nhiều hơn
        )
        print("✅ Agent đã được khởi tạo\n")
        
        # 4. Query từ đề bài
        query = """Tôi muốn lập kế hoạch du lịch tại Hồ Chí Minh trong ngày 08/04/2026. 
Hãy tư vấn:
1. Dự báo thời tiết trong thời gian này.
2. Gợi ý 3 khách sạn phù hợp với ngân sách 1.5 - 2 triệu VNĐ/đêm.
3. Trả thông tin chi tiết: tên khách sạn, địa chỉ, điểm đánh giá, giá phòng dự kiến."""
        
        print("📝 USER QUERY:")
        print("-" * 70)
        print(query)
        print("-" * 70)
        print()
        
        # 5. Chạy Agent
        print("🤔 Agent đang suy nghĩ và xử lý...\n")
        result = agent.run(query)
        
        # 6. Hiển thị kết quả
        print("\n" + "=" * 70)
        print("✅ KẾT QUẢ CUỐI CÙNG:")
        print("=" * 70)
        print(result)
        print("=" * 70)
        
        # 7. Thống kê
        print(f"\n📊 Thống kê:")
        print(f"   - Số bước thực hiện: {len(agent.history)}")
        print(f"   - Logs được lưu tại: ./logs/")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Người dùng đã dừng chương trình")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ LỖI: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
