# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Anh Tài
- **Student ID**: 2A202600388
- **Date**: 06/04/2026

---

## I. Technical Contribution (15 Points)

_Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.)._

- **Modules Implementated**: [`src/tools/hotel_tool`,`src/tools/weather_tool`,`src/agent/agent`, `src/tools/run_agent`, `src/core/ollama_provider`]
- **Code Highlights**: [Tích hợp tool lấy dựa trên api key lấy ra thời tiết, khách sạn. Tạo provider cho phép tải và import model ollama có trên máy cá nhân]
- **Documentation**: [Các công cụ này được gọi trong vòng lặp ReAct theo định dạng Thought → Action → Obs. LLM đọc prompt hệ thống, sinh suy luận bằng tiếng Việt, gọi tool tương ứng và dùng quan sát để quyết định bước tiếp theo.]

---

## II. Debugging Case Study (10 Points)

_Analyze a specific failure event you encountered during the lab using the logging system._

- **Problem Description**: [Tool lấy forecast weather bị lỗi do input thời gian không hợp lệ]
- **Log Source**: [Link or snippet from `logs/YYYY-MM-DD.log`]
- **Diagnosis**: [Why did the LLM do this? Was it the prompt, the model, or the tool spec?]
- **Solution**: [How did you fix it? (e.g., updated `Thought` examples in the system prompt)]

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

_Reflect on the reasoning capability difference._

1.  **Reasoning**:
    - Thought block giúp agent suy nghĩ từng bước, phân tách logic và hành động, giảm khả năng trả lời sai hoặc bỏ sót bước.
    - Chatbot trực tiếp trả lời thường bỏ qua việc kiểm tra từng công cụ hoặc chưa đánh giá điều kiện hiện tại.
2.  **Reliability**:
    - Agent đôi khi kém hơn Chatbot khi LLM sinh output không đúng định dạng action, dẫn đến tool không gọi được, hoặc khi tool API bị lỗi.
    - Chatbot trực tiếp trả lời vẫn cho kết quả nhanh nhưng không chính xác về số liệu thời gian thực
3.  **Observation**: Các observations từ tool giúp agent cập nhật thông tin thực tế, từ đó quyết định bước tiếp theo.

---

## IV. Future Improvements (5 Points)

_How would you scale this for a production-level AI agent system?_

- **Scalability**: [Cho phép agent xử lý song song nhiều yêu cầu người dùng, đồng thời quản lý trạng thái từng tác vụ để mở rộng quy mô lên hàng nghìn request mỗi phút.]
- **Safety**: [Thêm lớp kiểm soát hành vi, nơi mọi lệnh được agent sinh ra đều phải qua xác thực logic trước khi thực thi]
- **Performance**: [Tối ưu prompt và logic suy luận của LLM để giảm số bước cần thiết, tăng tốc độ trả lời mà vẫn đảm bảo chính xác]

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
