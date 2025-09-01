from __future__ import annotations

import threading
from prompt_toolkit.key_binding import KeyBindings
from ..core.cursor_client import get_global_cursor_client


def create_keybindings(on_text_submitted, on_newline) -> KeyBindings:
    kb = KeyBindings()

    @kb.add("c-c")
    def _(event) -> None:
        event.app.exit(result=None)

    @kb.add("c-d")
    def _(event) -> None:
        event.app.exit(result=None)

    @kb.add("c-j")
    def _(event) -> None:
        event.current_buffer.insert_text("\n")

    @kb.add("enter")
    def _(event) -> None:
        user_text = on_text_submitted()
        if not user_text:
            return
        client = get_global_cursor_client()
        def _on_chunk(t: str) -> None:
            on_newline(t)
        def _on_result(_t: str) -> None:
            pass
        th = threading.Thread(target=lambda: client.send_stream(user_text, on_chunk=_on_chunk, on_result=_on_result), daemon=True)
        th.start()

    return kb


__all__ = ["create_keybindings"]


