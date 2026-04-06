# Individual Report: Lab 3 - Chatbot vs ReAct Agent
**Student Name:** Trần Quang Long  
**Student ID:** 2A202600304  
**Date:** 2026-04-06

## I. Technical Contribution (15 Points)
Trong bài Lab này, tôi đã tham gia hoàn thiện cấu trúc cốt lõi của ReAct Agent và tích hợp các công cụ hỗ trợ truy xuất dữ liệu thực tế.

*   **Modules Implemented:** 
    *   `src/agent/agent.py`: Triển khai vòng lặp suy luận ReAct (Thought-Action-Observation).
    *   `src/tools/tools.py`: Xây dựng logic gọi API cho Weather và Hotel Search.
    *   `src/core/gemini_provider.py`: Tinh chỉnh cơ chế dừng (stop sequences) cho mô hình Gemini.
*   **Code Highlights:** 
    ```python
    # Ép LLM dừng lại để đợi dữ liệu từ Tool (trong gemini_provider.py)
    response = self.model.generate_content(
        full_prompt,
        generation_config=genai.types.GenerationConfig(
            stop_sequences=["Observation:"] 
        )
    )
    ```
*   **Documentation:** Code của tôi đóng vai trò là "cầu nối" giữa tư duy của LLM và thế giới thực. Khi LLM xuất ra chuỗi `Action:`, hàm `run` trong agent sẽ tạm dừng, bóc tách tham số JSON, gọi hàm Python tương ứng và trả về `Observation` để LLM tiếp tục suy luận dựa trên dữ liệu mới nhận được.

## II. Debugging Case Study (10 Points)
*   **Problem Description:** Agent gặp tình trạng "Ảo tưởng kết quả" (Hallucination). Thay vì dừng lại sau khi gọi `Action`, LLM tự ý viết luôn phần `Observation` giả định (ví dụ: tự bịa ra nhiệt độ -25°C) và đưa ra câu trả lời cuối cùng mà không thực sự gọi API.
*   **Log Source:** `--- Bước suy luận thứ 1 --- Thought: ... Action: get_weather_api(...) Observation: ... (Dữ liệu giả do LLM tự viết)`.
*   **Diagnosis:** Do mô hình Gemini 3.1 Flash quá thông minh và muốn tối ưu tốc độ, nó tự dự đoán kết quả mà nó cho là hợp lý thay vì tuân thủ quy trình chờ đợi phản hồi từ hệ thống.
*   **Solution:** Tôi đã áp dụng kỹ thuật **Stop Sequences** vào `GeminiProvider`. Bằng cách cấu hình cho mô hình dừng lại ngay khi xuất hiện từ khóa `"Observation:"`, tôi buộc LLM phải nhường quyền điều khiển cho mã nguồn Python để thực thi API thật.

## III. Personal Insights: Chatbot vs ReAct (10 Points)
*   **Reasoning:** Khối `Thought` đóng vai trò cực kỳ quan trọng. Nó giúp Agent tự phân tích các yêu cầu phức tạp (như vừa hỏi thời tiết, vừa tìm khách sạn) thành các bước nhỏ. So với Chatbot trả lời trực tiếp, ReAct Agent có khả năng "tự kiểm chứng" kế hoạch trước khi hành động.
*   **Reliability:** Agent hoạt động kém hơn Chatbot ở những câu hỏi mang tính cảm xúc hoặc trò chuyện phiếm (Chitchat), vì cấu trúc ReAct làm câu trả lời trở nên cứng nhắc và tốn thời gian xử lý hơn cho những việc không cần logic phức tạp.
*   **Observation:** Phản hồi từ môi trường là "chìa khóa" định hướng. Ví dụ, khi API khách sạn trả về danh sách trống (`data: []`), Agent đã ngay lập tức thay đổi chiến thuật: thay vì gợi ý khách sạn, nó chuyển sang giải thích về đặc thù địa lý của vùng Oymyakon để tư vấn cho người dùng.

## IV. Future Improvements (5 Points)
Để đưa hệ thống này lên mức Production, tôi đề xuất các cải tiến sau:
*   **Scalability:** Sử dụng **LangGraph** để quản lý các Agent có khả năng chạy song song nhiều Tool cùng lúc thay vì tuần tự, giúp giảm đáng kể thời gian chờ (Latency).
*   **Safety:** Triển khai một lớp **Guardrails** để kiểm tra tính hợp lệ của các tham số JSON trước khi truyền vào Tool, tránh việc LLM truyền sai định dạng gây sập hệ thống (Runtime Error).
*   **Performance:** Sử dụng **Semantic Caching** để lưu trữ các kết quả API thường xuyên được hỏi (như thời tiết tại các thành phố lớn), giúp tiết kiệm chi phí API và tăng tốc độ phản hồi cho người dùng.

---