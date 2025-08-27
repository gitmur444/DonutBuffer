"""
🤖 Agent Injector - Инжекция промптов в cursor-agent (новая версия)

Функционал:
- Подключение к уже запущенной сессии cursor-agent по session_id
- Отправка сообщений от имени пользователя (user role) в активную сессию
- Получение ответа ассистента и возврат результата вызывающему коду

Важно: этот класс НИЧЕГО не печатает. Отрисовкой занимаются уровни выше
(например, обработчики событий), чтобы избежать дублирования вывода.
"""

from typing import Optional, Callable
import sys
from pathlib import Path

# Импортируем из родительского пакета
sys.path.append(str(Path(__file__).parent.parent))
from ..core.base_wizard import BaseWizard
from ..core.cursor_client import get_global_cursor_client

class AgentInjector(BaseWizard):
    """Инжектор промптов в cursor-agent через центральный клиент."""

    def __init__(self) -> None:
        super().__init__()
        self._client = get_global_cursor_client()

    def attach_session(self, session_id: str) -> None:
        """Привязаться к уже запущенной сессии cursor-agent."""
        self._client.attach_session(session_id)

    def send_prompt(self, prompt: str) -> str:
        """Отправляет промпт и возвращает ответ ассистента как строку (без печати)."""
        chunks: list[str] = []

        def _on_chunk(t: str) -> None:
            chunks.append(t)

        def _on_result(_t: str) -> None:
            # итоговое событие зафиксировано; ответ уже собран из чанков
            pass

        ok = self._client.send_stream(prompt, on_chunk=_on_chunk, on_result=_on_result)
        return "".join(chunks) if ok else ""

    # Публичный API для стриминга с колбэками (без печати)
    def stream_with_callbacks(
        self,
        prompt: str,
        on_user: Optional[Callable[[str], None]] = None,
        on_chunk: Optional[Callable[[str], None]] = None,
        on_result: Optional[Callable[[str], None]] = None,
    ) -> bool:
        return self._client.send_stream(prompt, on_user=on_user, on_chunk=on_chunk, on_result=on_result)

    def check_cursor_agent_availability(self) -> bool:
        try:
            return self._client.available()
        except Exception:
            return False

    # Упрощённый fallback на запись в файл (при необходимости используй извне)
    def fallback_to_file_injection(self, prompt: str, name: str) -> bool:
        try:
            ambient_dir = Path.home() / ".cursor" / "ambient"
            ambient_dir.mkdir(parents=True, exist_ok=True)
            prompt_file = ambient_dir / f"{name}.md"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(prompt)
            return True
        except Exception:
            return False