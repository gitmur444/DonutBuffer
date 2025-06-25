"""
Базовый абстрактный класс для провайдеров LLM.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Абстрактный базовый класс для всех провайдеров LLM."""
    
    @abstractmethod
    def call_model(self, prompt: str, structured: bool = False) -> str:
        """Вызвать LLM модель с заданным промптом."""
        pass
