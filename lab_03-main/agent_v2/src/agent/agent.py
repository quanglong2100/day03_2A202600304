import os
import re
import json
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
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
        2. Format instructions: Thought, Action, Observation.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        
        return f"""Bạn là trợ lý AI thông minh có khả năng sử dụng tools để trả lời câu hỏi.

TOOLS KHẢ DỤNG:
{tool_descriptions}

CÁCH SỬ DỤNG:
1. Phân tích câu hỏi → Thought
2. Chọn tool và parameters → Action
3. Nhận kết quả → Observation
4. Lặp lại cho đến khi có đủ thông tin
5. Đưa ra câu trả lời cuối cùng → Final Answer

FORMAT BẮT BUỘC:
Thought: <suy nghĩ của bạn về bước tiếp theo>
Action: tool_name(param1="value1", param2="value2")
Observation: <kết quả sẽ được cung cấp>

Thought: <suy nghĩ tiếp theo>
Action: tool_name(...)
Observation: <kết quả>

Thought: <đã có đủ thông tin>
Final Answer: <câu trả lời hoàn chỉnh bằng tiếng Việt>

QUY TẮC:
- MỖI LẦN CHỈ GỌI 1 ACTION
- Action PHẢI đúng format: tool_name(param="value")
- KHÔNG tự viết Observation, hệ thống sẽ cung cấp
- Luôn kết thúc bằng "Final Answer:"
- Trả lời bằng tiếng Việt, chi tiết và hữu ích"""

    def run(self, user_input: str) -> str:
        """
        TODO: Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        # Initialize conversation
        conversation = f"Question: {user_input}\n\n"
        steps = 0
        
        print(f"\n{'='*70}")
        print(f"🤖 AGENT REASONING PROCESS")
        print(f"{'='*70}\n")

        while steps < self.max_steps:
            steps += 1
            print(f"\n--- Step {steps}/{self.max_steps} ---")
            
            # Generate LLM response
            try:
                response = self.llm.generate(conversation, system_prompt=self.get_system_prompt())
                
                # Handle different response formats
                if isinstance(response, dict):
                    llm_output = response.get('content', str(response))
                else:
                    llm_output = str(response)
                
                print(f"\n🧠 LLM Output:\n{llm_output[:300]}...")
                
            except Exception as e:
                error_msg = f"LLM generation error: {str(e)}"
                logger.log_event("AGENT_ERROR", {"error": error_msg, "step": steps})
                return f"Agent error: {error_msg}"
            
            # Check for Final Answer
            if "Final Answer:" in llm_output:
                final_answer = llm_output.split("Final Answer:")[-1].strip()
                logger.log_event("AGENT_END", {"steps": steps, "success": True})
                
                print(f"\n{'='*70}")
                print(f"✅ AGENT COMPLETED IN {steps} STEPS")
                print(f"{'='*70}\n")
                
                return final_answer
            
            # Parse Action
            action_match = re.search(r'Action:\s*(\w+)\((.*?)\)', llm_output, re.DOTALL)
            
            if action_match:
                tool_name = action_match.group(1).strip()
                args_str = action_match.group(2).strip()
                
                print(f"\n⚙️  Action detected: {tool_name}({args_str[:50]}...)")
                
                # Execute tool
                observation = self._execute_tool(tool_name, args_str)
                
                # Append to conversation
                conversation += f"{llm_output}\n"
                conversation += f"Observation: {observation}\n\n"
                
                # Log
                logger.log_event("TOOL_EXECUTED", {
                    "step": steps,
                    "tool": tool_name,
                    "args": args_str[:100]
                })
                
            else:
                # No action found, append and continue
                print(f"\n⚠️  No valid action found in this step")
                conversation += f"{llm_output}\n\n"
        
        # Max steps reached
        logger.log_event("AGENT_END", {"steps": steps, "success": False, "reason": "max_steps_reached"})
        
        print(f"\n{'='*70}")
        print(f"⚠️  AGENT STOPPED: Max steps ({self.max_steps}) reached")
        print(f"{'='*70}\n")
        
        return f"Agent không thể hoàn thành trong {self.max_steps} bước. Vui lòng thử lại với câu hỏi đơn giản hơn."

    def _execute_tool(self, tool_name: str, args_str: str) -> str:
        """
        Helper method to execute tools by name.
        TODO: Implement dynamic function calling or simple if/else
        """
        # Find tool
        tool = next((t for t in self.tools if t['name'] == tool_name), None)
        
        if not tool:
            error_msg = f"Tool '{tool_name}' not found. Available: {[t['name'] for t in self.tools]}"
            logger.log_event("TOOL_ERROR", {"error": error_msg})
            return error_msg
        
        try:
            # Parse arguments
            # Support formats: param1="value1", param2="value2" or user_query="..."
            args_dict = {}
            
            # Try JSON-like parsing first
            try:
                # Clean up args_str
                args_str_clean = args_str.strip()
                
                # Handle simple cases
                if not args_str_clean:
                    pass  # No args
                elif '=' in args_str_clean:
                    # Parse key=value pairs
                    # Match pattern: key="value" or key='value' or key=value
                    pattern = r'(\w+)\s*=\s*(["\'])(.*?)\2|(\w+)\s*=\s*(\w+)'
                    matches = re.findall(pattern, args_str_clean)
                    
                    for match in matches:
                        if match[0]:  # Quoted value
                            key = match[0]
                            value = match[2]
                        else:  # Unquoted value
                            key = match[3]
                            value = match[4]
                        
                        # Try to parse as int
                        try:
                            args_dict[key] = int(value)
                        except ValueError:
                            args_dict[key] = value
                else:
                    # Single positional argument (for simple cases)
                    args_dict = {"user_query": args_str_clean.strip('"').strip("'")}
            
            except Exception as parse_error:
                logger.log_event("ARG_PARSE_ERROR", {"error": str(parse_error), "args": args_str})
                return f"Error parsing arguments: {str(parse_error)}"
            
            print(f"   📋 Parsed args: {args_dict}")
            
            # Execute tool function
            result = tool['function'](**args_dict)
            
            # Format result
            result_str = str(result)
            print(f"   ✅ Tool result: {result_str[:200]}...")
            
            logger.log_event("TOOL_SUCCESS", {
                "tool": tool_name,
                "args": args_dict,
                "result_length": len(result_str)
            })
            
            return result_str
            
        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            logger.log_event("TOOL_EXECUTION_ERROR", {
                "tool": tool_name,
                "error": error_msg
            })
            print(f"   ❌ Error: {error_msg}")
            return error_msg
