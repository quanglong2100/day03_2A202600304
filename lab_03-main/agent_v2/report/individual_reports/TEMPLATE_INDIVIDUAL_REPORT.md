# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Hoang Ba Minh Quang
- **Student ID**: 2A202600063
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: /src/tools/analyze_intent_tools.py, /src/agent/agent.py
- **Code Highlights**: 
  - agent.py: class ReActAgent:
"""
ReAct-style Agent that follows the Thought-Action-Observation loop.
Implements full reasoning and tool execution cycle.
"""

def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 10):
    self.llm = llm
    self.tools = tools
    self.max_steps = max_steps
    self.history = []

def get_system_prompt(self) -> str:
    """
    TODO: Implement the system prompt that instructs the agent to follow ReAct.
    Should include:
    1. Available tools and their descriptions.
    2. Format instructions: Thought, Action, Observation....
  - analyze_intent_tool: class AnalyzeIntentTool:
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
    ...
- **Documentation**: 
 - analyze_intent_tool: Sau khi Agent nhận input, input sẽ được chuyển đến analyze_intent_tool để mô hình local phi-3 phân tích ý định của người dùng để trích xuất các tham số cần thiết rồi đưa vào các tools tiếp theo dưới dạng json. Bổ sung context thời gian (hôm nay/ngày mai) để xử lý các cụm như “ngày mai”, và chuẩn hóa định dạng
 - agent.py: đây là file điều hướng hoạt động của agent: cài đặt luồng ReAct và thiết kế system prompt. Trong đó luồng react giúp parse Action, gọi tool tương ứng, đưa Observation quay lại prompt cho bước tiếp theo. Bên cạnh đó còn tích hợp xây dựng system prompt liệt kê tools + format bắt buộc, giúp agent gọi tool đúng cú pháp và giảm sai lệch.

---

## II. Debugging Case Study (10 Points)

*Phân tích một lỗi cụ thể bạn gặp trong quá trình làm lab bằng hệ thống logging.*

- **Mô tả vấn đề**: Agent sinh tham số tool sai do bước trích xuất ý định (intent extraction) bị *hallucination*. Ví dụ user yêu cầu “Du lịch Phú Thọ vào ngày mai, khách sạn tối thiểu 5 triệu”, nhưng tool khách sạn lại bị gọi với `city="Thua Thien Hue"` và `budget_max=3000000` → kết quả trả về không đúng nhu cầu.
- **Nguồn log**: `logs/2026-04-06.log` (trích đoạn)
  ```json
  {"event":"AGENT_START","data":{"input":"Tôi muốn du lịch Phú Thọ vào ngày mai, gợi ý khách sạn tối thiểu 5 triệu"}}
  {"event":"TOOL_SUCCESS","data":{"tool":"analyze_intent"}}
  {"event":"TOOL_SUCCESS","data":{"tool":"search_hotels","args":{"city":"Thua Thien Hue","date":"2026-04-07","budget_max":3000000,"limit":3}}}
  ```
- **Chẩn đoán**: Nguyên nhân chính là lệch giữa prompt/model và ràng buộc của tool/API. Do API ngoài yêu cầu city theo dạng chuẩn hoá (ví dụ “Thua Thien Hue”), nên khi model không chắc chắn nó có xu hướng “snap” về địa danh quen thuộc. Đồng thời prompt ban đầu chưa quy định chặt ý nghĩa các cụm ngân sách tiếng Việt (ví dụ “tối thiểu X” phải map vào `budget_min`) và chưa có ngữ cảnh thời gian hiện tại để hiểu “ngày mai”, khiến JSON output vi phạm ràng buộc từ câu hỏi user.
- **Cách khắc phục**: Mình cải thiện `analyze_intent_tool` và guardrails của agent: (1) bổ sung context ngày hiện tại vào prompt để diễn giải “hôm nay/ngày mai”, (2) thêm rule + ví dụ cho parsing ngân sách (`<3 triệu` → `budget_max`, `tối thiểu 5 triệu` → `budget_min`), (3) ép output chỉ JSON, và (4) chỉnh system prompt để không bịa: nếu thiếu thông tin hoặc tham số trích xuất mâu thuẫn với input thì agent phải hỏi lại thay vì tự suy đoán.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Trong mô hình Chatbot truyền thống, LLM nhận input và sinh ra câu trả lời trực tiếp dựa trên trọng số nội bộ, điều này rất dễ sinh ra hallucination khi gặp dữ kiện khó hoặc sự kiện thời gian thực. Với kiến trúc ReAct, block Thought đóng vai trò như một bước "lập kế hoạch trước khi hành động" (chain-of-thought). Thay vì trả lời ngay, Agent bị buộc phải suy luận: "Người dùng hỏi 'thời tiết Sài Gòn ngày mai', mình không thể trả lời ngay. Mình cần dùng analyze_intent để chuẩn hóa 'Sài Gòn' thành 'Ho Chi Minh' giúp phù hợp với API Weather và tính toán ngày tháng thực tế cho 'ngày mai', sau đó mới gọi weather_tool". Nhờ block Thought, Agent chia nhỏ được các vấn đề phức tạp thành các bước giải quyết có tuần tự, giúp giải quyết những yêu cầu mơ hồ của người dùng và yêu cầu khắt khe của các external APIs.
2.  **Reliability**: Mặc dù thông minh hơn, ReAct Agent lại bộc lộ điểm yếu và hoạt động kém hiệu quả hơn Chatbot thông thường ở hai khía cạnh:
    - Độ trễ và Chi phí tính toán: Một câu hỏi đơn giản như "xin chào" hoặc câu hỏi kiến thức chung, chatbot chỉ mất 1-2 giây để phản hồi. Nhưng agent phải chạy qua một vòng lặp: sinh Thought -> gọi model local Phi-3 để kiểm tra intent -> sinh Observation -> gọi model Gemini. Việc này làm tăng độ trễ lên đáng kể (thường mất 6-10 giây) và lãng phí tài nguyên cho những tác vụ không cần đến external tools.
    - Tính dễ vỡ của hệ thống: Agent phụ thuộc hoàn toàn vào format. Nếu mô hình local Phi-3 trong analyze_intent phân tích sai hoặc không trả về đúng định dạng JSON chuẩn xác, bộ parser trong agent.py sẽ bị lỗi. Lúc này, hệ thống có thể bị crash hoặc rơi vào vòng lặp vô hạn khiến chạy hết số lần lặp mà không đưa ra được câu trả lời.
3.  **Observation**: giúp AI bám vào thông tin thực. Trong quá trình test, nếu không có Observation, LLM sẽ tự bịa ra thông tin để làm hài lòng người dùng. Khi áp dụng ReAct, Observation mang về kết quả thực tế từ môi trường. Ví dụ: Khi Agent gọi tool tìm khách sạn với ngân sách quá thấp (vd: 200k tại trung tâm Hà Nội), API trả về mảng rỗng. Lúc này, bước đưa thông tin rỗng ngược lại vào prompt. Nhờ đó, bước thought tiếp theo của Agent sẽ thay đổi chiến lược dựa trên ngữ cnahr nhận được

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: 
- - Tách agent thành các service độc lập: API Gateway (chat), Orchestrator (ReAct loop), Tool Workers.
- - Dùng asynchronous queue ****cho tool calls và long-running tasks (weather/hotel search), hỗ trợ retry, rate-limit, và horizontal scaling.
- - Thêm state store để lưu conversation state, tool results cache, và hỗ trợ multi-turn + resume session.
- **Safety**:
- - Áp dụng tool permissioning: allowlist tools, validate schema đầu vào/đầu ra, chặn prompt injection vào tool args.
- - Thêm lớp Supervisor/Guardrail: kiểm tra action trước khi execute (ví dụ: gọi API đúng domain, budget/date hợp lệ), và kiểm tra output để tránh hallucination (đặc biệt với intent extraction).
- **Performance**:
- - Dùng caching cho các kết quả phổ biến (thời tiết, danh sách khách sạn theo bbox/date) + TTL phù hợp, giảm số lần gọi API.
- - Tối ưu LLM usage: prompt templates ngắn gọn, response parsing chắc chắn (structured output / JSON mode), và dùng model nhỏ cho intent extraction, model lớn cho final response.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
