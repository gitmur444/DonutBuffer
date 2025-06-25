"""
Провайдер для локальной модели Ollama.
"""

import json
import logging
import requests
from typing import Dict, Any

from .provider_base import LLMProvider

logger = logging.getLogger('llm')


class OllamaProvider(LLMProvider):
    """Провайдер для локальной модели Ollama."""
    
    def __init__(self, model: str = "llama3"):
        self.model = model
        self.api_url = "http://localhost:11434/api/generate"
    
    def call_model(self, prompt: str, structured: bool = False) -> str:
        """Вызвать Ollama LLM и вернуть ответ в виде строки."""
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        if structured:
            payload["format"] = "json"
        
        try:
            resp = requests.post(self.api_url, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")
        except Exception as e:
            logger.error(f"Ошибка при вызове Ollama API: {e}")
            raise
