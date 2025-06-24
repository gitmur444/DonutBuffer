"""
Recognition module for identifying user intents and extracting parameters for DonutBuffer.
"""

import json
import logging
from typing import Dict, Any

from .llm import call_llm

# Настройка логирования
logger = logging.getLogger('recognizer')

def detect_intent(text: str) -> str:
    """
    Ask the LLM to classify the user command into one of the intents.
    Returns one of: modify_code, shell_command, generate_script, ask_question, run_program
    """
    logger.info(f"Определение намерения для текста: '{text}'")
    
    prompt = (
        "Classify the following command into one of the intents: "
        "[modify_code, shell_command, generate_script, ask_question, run_program].\n"
        "run_program intent should be used when the user wants to run or start a buffer implementation.\n"
        f"Command: {text}\n"
        'Respond with JSON: {"intent": "<intent>"}'
    )
    response = call_llm(prompt, structured=True)
    
    try:
        obj = json.loads(response)
        intent = obj.get("intent", "ask_question")
        logger.info(f"Определено намерение: '{intent}'")
        return intent
    except Exception as e:
        logger.error(f"Ошибка разбора JSON ответа: {e}. Возвращаем намерение по умолчанию.")
        return "ask_question"


def detect_buffer_type(user_prompt: str) -> str:
    """
    Detect which type of buffer implementation to run based on user prompt.
    Returns one of: 'lockfree', 'mutex', 'concurrent_queue'
    """
    logger.info(f"Определение типа буфера для запроса: '{user_prompt}'")
    
    prompt = (
        "Based on the user command, determine which type of ring buffer implementation "
        "should be run. Choose one of these types exactly: "
        "[lockfree, mutex, concurrent_queue].\n"
        f"Command: {user_prompt}\n"
        'Respond with JSON: {"buffer_type": "<type>"}'
    )
    response = call_llm(prompt, structured=True)
    
    try:
        obj = json.loads(response)
        buffer_type = obj.get("buffer_type", "mutex")
        logger.info(f"Определен тип буфера: '{buffer_type}'")
        return buffer_type
    except Exception as e:
        logger.error(f"Ошибка разбора JSON ответа: {e}. Возвращаем тип буфера по умолчанию.")
        # Default to mutex if parsing fails
        return "mutex"


def extract_buffer_parameters(user_prompt: str, buffer_type: str) -> Dict[str, Any]:
    """
    Extract parameters for the buffer from user prompt.
    Returns a dictionary with parameters according to RingBufferConfig structure:
    - buffer_type (automatically set from detect_buffer_type)
    - producer_count
    - consumer_count
    - buffer_size_mb
    - total_transfer_mb
    """
    logger.info(f"Извлечение параметров для буфера '{buffer_type}' из запроса: '{user_prompt}'")
    
    prompt = (
        f"Extract parameters for running a {buffer_type} ring buffer from the following command: "
        f"\"{user_prompt}\". "
        "Extract the following parameters according to the RingBufferConfig structure:\n"
        "- producer_count: Number of producers\n"
        "- consumer_count: Number of consumers\n"
        "- buffer_size_mb: Size of the buffer in megabytes\n"
        "- total_transfer_mb: Total amount of data to transfer in megabytes\n\n"
        "Respond with JSON format. Use default values if not specified in the command:"
        "{\"producer_count\": 1, \"consumer_count\": 1, \"buffer_size_mb\": 1, \"total_transfer_mb\": 100}"
    )
    response = call_llm(prompt, structured=True)
    
    try:
        params = json.loads(response)
        logger.info(f"Извлечены параметры: {params}")
            
        # Add buffer_type to parameters
        params["buffer_type"] = buffer_type
        
        # Ensure all required parameters have default values if not specified
        default_params = {
            "producer_count": 1, 
            "consumer_count": 1, 
            "buffer_size_mb": 1, 
            "total_transfer_mb": 100
        }
        
        for key, value in default_params.items():
            if key not in params:
                params[key] = value
                
        return params
    except Exception as e:
        logger.error(f"Ошибка разбора JSON ответа: {e}. Возвращаем параметры по умолчанию.")
        # Return default parameters if parsing fails
        default_params = {
            "buffer_type": buffer_type,
            "producer_count": 1, 
            "consumer_count": 1, 
            "buffer_size_mb": 1, 
            "total_transfer_mb": 100
        }
        logger.info(f"Используем параметры по умолчанию: {default_params}")
        return default_params


def get_buffer_info(user_prompt: str) -> Dict[str, Any]:
    """
    Returns complete information about which buffer program to run,
    including buffer type and parameters.
    """
    buffer_type = detect_buffer_type(user_prompt)
    return {
        "buffer_type": buffer_type,
        "command": f"./run_{buffer_type}_buffer",
        "parameters": extract_buffer_parameters(user_prompt, buffer_type)
    }
