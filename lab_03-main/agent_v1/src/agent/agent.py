import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.core.ollama_provider import OllamaProvider

class ReActAgent:
    """
    SKELETON: A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Students should implement the core loop logic and tool execution.
    """
    
    def __init__(self, llm: OllamaProvider, tools: list, max_steps: int = 5):
        self.llm = llm  # Bây giờ llm chính là một instance của OllamaProvider
        self.tools = tools
        self.max_steps = max_steps

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
        Bạn là một trợ lý thông minh. Hãy giải quyết yêu cầu của người dùng theo từng bước suy luận.
        Các công cụ bạn có:
        {tool_descriptions}

        QUY TẮC TRÌNH BÀY (BẮT BUỘC):
        1. Sử dụng TIẾNG VIỆT hoàn toàn cho mọi suy luận.
        2. Tuân thủ chính xác định dạng sau cho mỗi bước:
        Suy nghĩ: Bạn đang định làm gì và tại sao?
        Hành động: tên_hàm(tham_số)
        Quan sát: Kết quả trả về từ công cụ.
        3. Khi đã đủ thông tin, kết thúc bằng:
        Kết luận cuối cùng: Câu trả lời đầy đủ cho người dùng.

        Ví dụ:
        Suy nghĩ: Tôi cần kiểm tra thời tiết Hà Nội trước.
        Hành động: get_weather("Hà Nội")
        Quan sát: 25 độ C, trời đẹp.
        ...
        Kết luận cuối cùng: Thời tiết Hà Nội đang rất đẹp, phù hợp để đi chơi.
        """

    # def run(self, user_input: str) -> str:
    #     logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})

    #     prompt = user_input
    #     steps = 0

    #     while steps < self.max_steps:
    #         steps += 1

    #         result = self.llm.generate(
    #             prompt,
    #             system_prompt=self.get_system_prompt()
    #         )

    #         print(result)  # để debug thấy reasoning

    #         # Nếu có Final Answer -> dừng
    #         if "Final Answer:" in result:
    #             logger.log_event("AGENT_END", {"steps": steps})
    #             return result

    #         # Parse Action
    #         action_match = re.search(r"Action\s*\d*:\s*(\w+)\((.*?)\)", result)

    #         if not action_match:
    #             prompt += "\nObservation: No action detected."
    #             continue

    #         tool_name = action_match.group(1)
    #         args = action_match.group(2).strip().replace('"', "")

    #         observation = self._execute_tool(tool_name, args)

    #         prompt += f"\n{result}\nObservation {steps}: {observation}\n"

    #     logger.log_event("AGENT_END", {"steps": steps})
    #     return "Agent stopped: max steps reached."
    

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})

        # Giữ nguyên việc khởi tạo prompt
        prompt = f"Yêu cầu từ người dùng: {user_input}\nLưu ý: Luôn suy nghĩ và trả lời bằng tiếng Việt."
        steps = 0

        while steps < self.max_steps:
            steps += 1

            result = self.llm.generate(
                prompt,
                system_prompt=self.get_system_prompt()
            )

            # Hiển thị rõ ràng từng bước suy luận ra màn hình
            print(f"\n--- BƯỚC {steps} ---")
            print(result) 

            # Kiểm tra Kết luận cuối cùng (Thay cho Final Answer)
            if "Kết luận cuối cùng:" in result:
                logger.log_event("AGENT_END", {"steps": steps})
                return result.split("Kết luận cuối cùng:")[-1].strip()

            # Parse Action với từ khóa tiếng Việt "Hành động"
            # Regex này bắt được cả "Hành động:", "Action:", "Hành động 1:"
            action_match = re.search(r"(?:Hành động|Action)\s*\d*:\s*(\w+)\((.*?)\)", result)

            if not action_match:
                prompt += f"\n{result}\nQuan sát: Không tìm thấy hành động hợp lệ. Hãy sử dụng đúng định dạng tiếng Việt."
                continue

            tool_name = action_match.group(1)
            args = action_match.group(2).strip().replace('"', "").replace("'", "")

            # Thực thi công cụ (Giữ nguyên logic cũ)
            observation = self._execute_tool(tool_name, args)

            # In kết quả quan sát ra màn hình để người dùng theo dõi
            print(f"Quan sát: {observation}")

            # Nối vào prompt để lặp lại vòng lặp (Giữ nguyên logic nối chuỗi)
            # Thêm từ khóa "Suy nghĩ:" để mồi LLM viết tiếp bằng tiếng Việt
            prompt += f"\n{result}\nQuan sát: {observation}\nSuy nghĩ: "

        logger.log_event("AGENT_END", {"steps": steps})
        return "Agent dừng: Đã đạt số bước tối đa."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        for tool in self.tools:
            if tool["name"] == tool_name:
                try:
                    return tool["func"](args)
                except Exception as e:
                    return f"Tool execution failed: {str(e)}"

        return f"Tool {tool_name} not found."
