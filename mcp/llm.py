import json
import logging
import os
from typing import Optional

# Импортируем классы провайдеров из нового пакета
from .providers import LLMProvider, OllamaProvider, OpenAIProvider

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('llm')

# Отключение логов httpx (используется OpenAI API)
logging.getLogger('httpx').setLevel(logging.WARNING)


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
    logger.info(f"DonutBuffer >> LLM: {prompt}")
    logger.debug(f"Полный запрос к LLM: {prompt}")
    
    # Вызываем провайдера
    response = current_provider.call_model(prompt, structured)
    
    # Логируем ответ от LLM
    logger.info(f"LLM >> DonutBuffer: {response}")
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
