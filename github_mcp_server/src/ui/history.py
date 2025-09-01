from __future__ import annotations

import textwrap
from typing import List, Tuple
from prompt_toolkit.layout.controls import FormattedTextControl


class MessageHistory:
    """Хранилище истории сообщений с рендерингом в FormattedTextControl."""

    def __init__(self, initial_system_text: str = "") -> None:
        self._messages: List[Tuple[str, str]] = []
        if initial_system_text:
            self._messages.append(("system", initial_system_text))
        self.control = FormattedTextControl(text="")

    def append_user(self, text: str) -> None:
        self._messages.append(("user", text))

    def append_assistant_chunk(self, text: str) -> None:
        if not self._messages or self._messages[-1][0] != "assistant":
            self._messages.append(("assistant", text))
        else:
            role, cur = self._messages[-1]
            self._messages[-1] = (role, cur + text)

    def _compose_text(self) -> str:
        parts: List[str] = []
        for _role, text in self._messages:
            parts.append(text)
            if not text.endswith("\n"):
                parts.append("\n")
        return "".join(parts)

    def update_view(self, columns: int) -> None:
        # columns используются косвенно для корректного расчёта высоты выше по стеку
        self.control.text = self._compose_text()

    def rendered_lines_count(self, columns: int) -> int:
        text = self.control.text or ""
        if not text:
            return 0
        count = 0
        for line in text.splitlines() or [""]:
            wraps = textwrap.wrap(line, width=max(1, columns)) or [""]
            count += max(1, len(wraps))
        return count


__all__ = ["MessageHistory"]


