"""
UIEventBus: простой потокобезопасный шина для доставки сообщений ассистента в UI.

Ambient/handlers публикуют текст через publish_assistant_message(text),
UI регистрирует consumer для приёма сообщений.
"""

from __future__ import annotations

import threading
from typing import Callable, Optional, List


class UIEventBus:
    _instance: Optional["UIEventBus"] = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self._consumer: Optional[Callable[[str], None]] = None
        self._buffer: List[str] = []
        self._mtx = threading.Lock()

    @classmethod
    def instance(cls) -> "UIEventBus":
        with cls._lock:
            if cls._instance is None:
                cls._instance = UIEventBus()
            return cls._instance

    def set_consumer(self, consumer: Optional[Callable[[str], None]]) -> None:
        with self._mtx:
            self._consumer = consumer
            if consumer and self._buffer:
                for msg in self._buffer:
                    try:
                        consumer(msg)
                    except Exception:
                        pass
                self._buffer.clear()

    def publish_assistant_message(self, text: str) -> None:
        if not isinstance(text, str) or text == "":
            return
        with self._mtx:
            if self._consumer:
                try:
                    self._consumer(text)
                except Exception:
                    # На всякий случай не теряем сообщение
                    self._buffer.append(text)
            else:
                self._buffer.append(text)


__all__ = ["UIEventBus"]


