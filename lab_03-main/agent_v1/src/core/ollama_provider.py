import requests
import json
from typing import Optional, Generator

class OllamaProvider:
    def __init__(self, model_name: str, host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        endpoint = f"{self.host}/api/generate"
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "stop": ["Observation:"]
            }
        }

        try:
            response = requests.post(endpoint, json=payload, timeout=60)
            response.raise_for_status()
            result_json = response.json()
            return result_json.get("response", "").strip()
            
        except Exception as e:
            return f"Error inside OllamaProvider: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        endpoint = f"{self.host}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True
        }
        
        try:
            with requests.post(endpoint, json=payload, stream=True) as response:
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        yield chunk.get("response", "")
        except Exception as e:
            yield f"Stream Error: {str(e)}"