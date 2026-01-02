import streamlit as st
import requests
import json
from typing import List, Dict, Generator

class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
    
    def get_models(self) -> List[str]:
        """Get available Ollama models"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return [m["name"] for m in response.json().get("models", [])]
        except:
            return []
    
    def is_running(self) -> bool:
        """Check if Ollama server is running"""
        try:
            requests.get(f"{self.host}/api/tags", timeout=5)
            return True
        except:
            return False
    
    def generate(self, messages: List[Dict], model: str = "llama3.2") -> Generator[str, None, None]:
        """Stream response from Ollama"""
        url = f"{self.host}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": 0.1, "top_p": 0.9, "num_predict": 2048}
        }
        
        response = requests.post(url, json=payload, stream=True)
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                if content := data.get("message", {}).get("content"):
                    full_response += content
                    yield content
        
        yield full_response  # Final complete response

# Global client instance
ollama = OllamaClient()
