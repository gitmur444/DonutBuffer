import json
from typing import Optional
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def call_llm(prompt: str, *, structured: bool = False) -> str:
    """Call local Ollama LLM and return its response as a string."""
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    if structured:
        payload["format"] = "json"
    resp = requests.post(OLLAMA_URL, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Ollama returns {"response": "..."}
    return data.get("response", "")


def detect_intent(text: str) -> str:
    """Ask the LLM to classify the user command into one of the intents."""
    prompt = (
        "Classify the following command into one of the intents: "
        "[modify_code, shell_command, generate_script, ask_question].\n"
        f"Command: {text}\n"
        'Respond with JSON: {"intent": "<intent>"}'
    )
    response = call_llm(prompt, structured=True)
    try:
        obj = json.loads(response)
        return obj.get("intent", "ask_question")
    except Exception:
        return "ask_question"


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
