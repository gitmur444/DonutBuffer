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
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
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

        # Border controls (text-based) to ensure exact reflow on resize
        self._top_ctrl = FormattedTextControl(text="")
        self._bottom_ctrl = FormattedTextControl(text="")
        self.frame_top = Window(content=self._top_ctrl, height=D.exact(1), dont_extend_height=True)
        self.frame_bottom = Window(content=self._bottom_ctrl, height=D.exact(1), dont_extend_height=True)

        # Vertical borders with explicit height matching the input box
        self.left_border = Window(width=1, char="│", dont_extend_height=True)
        self.right_border = Window(width=1, char="│", dont_extend_height=True)

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
            layout=Layout(HSplit([
                self.frame_top,
                VSplit([self.left_border, self.input_window, self.right_border]),
                self.frame_bottom,
            ])),
            key_bindings=self.kb,
            mouse_support=False,
            full_screen=False,
            style=self.style,
            refresh_interval=0.2,
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
        # Inner width excludes vertical borders; BufferControl accounts for prompt prefix
        inner_width = max(1, columns - 2)
        text = self.buffer.text
        lines = text.split("\n") if text != "" else [""]
        needed = 0
        for line in lines:
            wraps = textwrap.wrap(line, width=inner_width) or [""]
            needed += max(1, len(wraps))
        box_height = max(1, needed)
        self.input_window.height = D.exact(box_height)
        self.left_border.height = D.exact(box_height)
        self.right_border.height = D.exact(box_height)
        # Redraw top/bottom borders to current width
        self._draw_borders(columns)
        self._invalidate()

    def _draw_borders(self, columns: int) -> None:
        cols = max(4, columns)
        top = "┌" + "─" * max(2, cols - 2) + "┐"
        bottom = "└" + "─" * max(2, cols - 2) + "┘"
        self._top_ctrl.text = top
        self._bottom_ctrl.text = bottom

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

