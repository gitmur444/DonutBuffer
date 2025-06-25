"""
Провайдер для OpenAI API.
"""

import json
import logging
import os
import openai
from typing import Dict, Any, List

from .provider_base import LLMProvider

logger = logging.getLogger('llm')


class OpenAIProvider(LLMProvider):
    """Провайдер для OpenAI API."""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        openai.api_key = api_key
    
    def call_model(self, prompt: str, structured: bool = False) -> str:
        """Вызвать OpenAI API и вернуть ответ в виде строки."""
        try:
            if structured:
                system_message = "Respond only with valid JSON with no explanations or additional text."
                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ]
            else:
                messages = [{"role": "user", "content": prompt}]
                
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1 if structured else 0.7,
                response_format={"type": "json_object"} if structured else None
            )
            
            content = response.choices[0].message.content
            
            # Проверяем, что для structured запросов получен валидный JSON
            if structured:
                try:
                    # Проверка валидности JSON
                    json.loads(content)
                except json.JSONDecodeError:
                    logger.warning(f"OpenAI вернул невалидный JSON: {content}")
                    # Оборачиваем простой ответ в JSON если это просто строка без кавычек
                    if '"' not in content and '{' not in content and '[' not in content:
                        return json.dumps({"intent": content.strip()})
                    
            return content
        except Exception as e:
            logger.error(f"Ошибка при вызове OpenAI API: {e}")
            raise
