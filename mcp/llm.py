import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

import requests
import openai

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('llm')


class LLMProvider(ABC):
    """Абстрактный базовый класс для всех провайдеров LLM."""
    
    @abstractmethod
    def call_model(self, prompt: str, structured: bool = False) -> str:
        """Вызвать LLM модель с заданным промптом."""
        pass


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
            response = openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1 if structured else 0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Ошибка при вызове OpenAI API: {e}")
            raise


# Глобальный провайдер
current_provider = None


def init_provider(provider_name: str = None) -> None:
    """Инициализировать провайдера LLM."""
    global current_provider
    
    if not provider_name:
        provider_name = os.environ.get("LLM_PROVIDER", "ollama").lower()
    else:
        provider_name = provider_name.lower()
    
    logger.info(f"Инициализация провайдера LLM: {provider_name}")
    
    if provider_name == "ollama":
        model = os.environ.get("OLLAMA_MODEL", "llama3")
        current_provider = OllamaProvider(model)
        logger.info(f"Используется Ollama с моделью {model}")
    elif provider_name == "openai":
        model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
        current_provider = OpenAIProvider(model)
        logger.info(f"Используется OpenAI с моделью {model}")
    else:
        raise ValueError(f"Неизвестный провайдер LLM: {provider_name}")


def call_llm(prompt: str, *, structured: bool = False) -> str:
    """Вызвать LLM и вернуть ответ в виде строки."""
    global current_provider
    
    # Инициализируем провайдера, если он еще не инициализирован
    if current_provider is None:
        init_provider()
    
    # Логируем запрос к LLM
    truncated_prompt = prompt[:100] + '...' if len(prompt) > 100 else prompt
    logger.info(f"LLM запрос: {truncated_prompt}")
    logger.debug(f"Полный запрос к LLM: {prompt}")
    
    # Вызываем провайдера
    response = current_provider.call_model(prompt, structured)
    
    # Логируем ответ от LLM
    truncated_response = response[:100] + '...' if len(response) > 100 else response
    logger.info(f"LLM ответ: {truncated_response}")
    logger.debug(f"Полный ответ LLM: {response}")
    
    return response


def generate_patch(user_prompt: str) -> str:
    prompt = (
        "You are a coding assistant. Generate a unified diff patch for the file "
        "ring_buffer.cpp located in the current directory to satisfy the user request."
        "Respond only with the patch.\n"
        f"User request: {user_prompt}"
    )
    return call_llm(prompt)


def generate_shell_command(user_prompt: str) -> str:
    prompt = (
        "Generate a safe shell command for the following request. Respond with the "
        "command only.\nRequest: " + user_prompt
    )
    return call_llm(prompt)


def generate_script(user_prompt: str) -> dict:
    prompt = (
        "Create a small script based on the user request. Respond with JSON:"
        ' {"filename":..., "language":"bash|python", "run":true|false, '
        '"content": '
        "<script contents>"
        "}.\nRequest: " + user_prompt
    )
    response = call_llm(prompt, structured=True)
    try:
        return json.loads(response)
    except Exception:
        return {}


def answer_question(user_prompt: str) -> str:
    return call_llm(user_prompt)


# Функция detect_buffer_type перемещена в модуль recognizer.py


# Функция run_buffer_program перемещена и переименована в get_buffer_info в модуле recognizer.py


# Функция extract_buffer_parameters перемещена в модуль recognizer.py
