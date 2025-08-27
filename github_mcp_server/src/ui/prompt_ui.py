"""
Prompt Toolkit based single-frame multi-line input UI with dynamic placeholder
and automatic height adjustment on text changes and terminal resize.
"""

from __future__ import annotations

import asyncio
import textwrap
from typing import List

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.containers import VSplit
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.styles import Style

from .constants import PLACEHOLDER, DEFAULT_STYLE_DICT


class DynamicPromptUI:
    def __init__(self) -> None:
        self.placeholder_active = True

        self.buffer = Buffer(multiline=True)
        self.buffer.on_text_changed += self._on_text_changed

        self.input_window = Window(
            content=BufferControl(
                buffer=self.buffer,
                input_processors=[BeforeInput(self._before_input)],
                focusable=True,
            ),
            wrap_lines=True,
            height=D(preferred=1),
        )

        # Borders built from char-filled windows so they auto-resize with the terminal
        self.top_left = Window(height=1, width=1, char="┌")
        self.top_line = Window(height=1, char="─")
        self.top_right = Window(height=1, width=1, char="┐")

        self.left_border = Window(width=1, char="│")
        self.right_border = Window(width=1, char="│")

        self.bottom_left = Window(height=1, width=1, char="└")
        self.bottom_line = Window(height=1, char="─")
        self.bottom_right = Window(height=1, width=1, char="┘")

        self.kb = KeyBindings()

        @self.kb.add("c-c")
        def _(event) -> None:
            event.app.exit(result=None)

        @self.kb.add("c-d")
        def _(event) -> None:
            event.app.exit(result=self.buffer.text)

        @self.kb.add("c-j")
        def _(event) -> None:
            event.current_buffer.insert_text("\n")

        @self.kb.add("enter")
        def _(event) -> None:
            event.app.exit(result=self.buffer.text)

        self.style = Style.from_dict(DEFAULT_STYLE_DICT)

        self.app = Application(
            layout=Layout(
                HSplit(
                    [
                        VSplit([self.top_left, self.top_line, self.top_right], height=1),
                        VSplit([self.left_border, self.input_window, self.right_border]),
                        VSplit([self.bottom_left, self.bottom_line, self.bottom_right], height=1),
                    ]
                )
            ),
            key_bindings=self.kb,
            mouse_support=False,
            full_screen=False,
            style=self.style,
        )

        # Background tasks must be created when an event loop is running.
        # We schedule the watcher in run(pre_run=...) instead of here.
        self._invalidate()

    def _before_input(self):
        if self.placeholder_active:
            return [("class:prompt", "→ "), ("class:placeholder", PLACEHOLDER)]
        return [("class:prompt", "→ ")]

    def _on_text_changed(self, _event) -> None:
        self.placeholder_active = len(self.buffer.text) == 0
        self._recompute_height()

    def _invalidate(self) -> None:
        get_app().invalidate()

    def _recompute_height(self) -> None:
        app = get_app()
        columns = max(10, app.output.get_size().columns)
        # Compute inner width: remove only vertical borders. The prompt prefix
        # is rendered by BeforeInput and already accounted for by prompt_toolkit
        # when wrapping; subtracting it here leads to mismatch on resize.
        inner_width = max(1, columns - 2)  # -2 for left/right borders only
        text = self.buffer.text or ""
        if not text:
            needed = 1
        else:
            needed = 0
            for line in text.splitlines() or [""]:
                wrapped: List[str] = textwrap.wrap(line, width=max(1, inner_width)) or [""]
                needed += len(wrapped)
        self.input_window.height = D(preferred=max(1, needed))
        self._invalidate()

    async def _resize_watcher(self) -> None:
        app = self.app
        last_size = app.output.get_size()
        while True:
            await asyncio.sleep(0.15)
            size = app.output.get_size()
            if size.columns != last_size.columns or size.rows != last_size.rows:
                last_size = size
                self._recompute_height()

    def run(self) -> str | None:
        self._recompute_height()
        # Create the background task after the event loop is running
        def _pre_run() -> None:
            self.app.create_background_task(self._resize_watcher())
        return self.app.run(pre_run=_pre_run)


__all__ = ["DynamicPromptUI"]

