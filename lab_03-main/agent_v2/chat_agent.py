"""
Interactive Chat với Travel Planning Agent
Cho phép chat liên tục với agent
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.core.openai_provider import OpenAIProvider
from src.core.gemini_provider import GeminiProvider
from src.core.local_provider import LocalProvider
from src.agent.agent import ReActAgent
from src.tools.registry import get_available_tools

# Load environment variables
load_dotenv()


def get_llm_provider(provider_name: str = None):
    """Khởi tạo LLM provider theo config"""
    if provider_name is None:
        provider_name = os.getenv("DEFAULT_PROVIDER", "gemini")
    
    print(f"🤖 Đang khởi tạo LLM Provider: {provider_name}")
    
    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_openai_api_key_here":
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
    """Interactive chat loop"""
    
    print("=" * 70)
    print("🌍 TRAVEL PLANNING AGENT - Interactive Chat")
    print("=" * 70)
    
    try:
        # 1. Khởi tạo LLM Provider
        llm = get_llm_provider()
        print(f"✅ LLM Provider đã sẵn sàng: {llm.model_name}\n")
        
        # 2. Lấy danh sách tools
        tools = get_available_tools()
        print(f"🛠️  Đã load {len(tools)} tools")
        print()
        
        # 3. Khởi tạo ReAct Agent
        agent = ReActAgent(
            llm=llm,
            tools=tools,
            max_steps=10
        )
        print("✅ Agent đã được khởi tạo\n")
        
        # 4. Chat loop
        print("=" * 70)
        print("💬 BẮT ĐẦU CHAT (gõ 'exit' hoặc 'quit' để thoát)")
        print("=" * 70)
        print()
        
        print("Ví dụ câu hỏi:")
        print("  - Tôi muốn đi du lịch Hà Nội ngày 10/04/2026, gợi ý khách sạn 2-3 triệu")
        print("  - Thời tiết Đà Nẵng hôm nay thế nào?")
        print("  - Tìm 5 khách sạn ở Hồ Chí Minh trong khoảng 1.5-2 triệu")
        print()
        
        conversation_count = 0
        
        while True:
            # Get user input
            try:
                user_input = input(f"\n👤 Bạn: ").strip()
            except KeyboardInterrupt:
                print("\n\n👋 Tạm biệt!")
                break
            
            # Check exit commands
            if user_input.lower() in ['exit', 'quit', 'bye', 'thoát']:
                print("\n👋 Cảm ơn bạn đã sử dụng Travel Planning Agent!")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            conversation_count += 1
            print(f"\n{'─' * 70}")
            print(f"Conversation #{conversation_count}")
            print(f"{'─' * 70}")
            
            # Run agent
            try:
                result = agent.run(user_input)
                
                # Display result
                print(f"\n{'=' * 70}")
                print(f"🤖 Agent:")
                print(f"{'=' * 70}")
                print(result)
                print(f"{'=' * 70}")
                
            except Exception as e:
                print(f"\n❌ LỖI: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n📊 Thống kê session:")
        print(f"   - Tổng số conversations: {conversation_count}")
        print(f"   - Logs được lưu tại: ./logs/")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Chat interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ LỖI KHỞI TẠO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
