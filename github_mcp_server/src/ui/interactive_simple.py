#!/usr/bin/env python3
"""
Interactive CLI using prompt_toolkit with dynamic single-line frame prompt.
- Full frame visible at start
- Placeholder "→ Plan, search, build anything" in gray until typing
- Only "→" remains once user starts typing
- Auto-expands vertically as text wraps or on explicit newline
- Adjusts to terminal resize, wrapping content accordingly
"""

# Removed asyncio import as async functionality was removed
import json
import os
import signal
import subprocess
import sys
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


PLACEHOLDER = "Plan, search, build anything"


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

        # Borders
        self.top_border = Window(height=1)
        self.left_border = Window(width=1)
        self.right_border = Window(width=1)
        self.bottom_border = Window(height=1)

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

        self.style = Style.from_dict({
            "prompt": "bold",
            "placeholder": "#888888 italic",
        })

        self.app = Application(
            layout=Layout(
                HSplit(
                    [
                        self.top_border,
                        VSplit([self.left_border, self.input_window, self.right_border]),
                        self.bottom_border,
                    ]
                )
            ),
            key_bindings=self.kb,
            mouse_support=False,
            full_screen=False,
            style=self.style,
        )

# Removed problematic async background task
        self._redraw_frame()

    def _before_input(self):
        if self.placeholder_active:
            return [("class:prompt", "→ "), ("class:placeholder", PLACEHOLDER)]
        return [("class:prompt", "→ ")]

    def _on_text_changed(self, _event) -> None:
        self.placeholder_active = len(self.buffer.text) == 0
        self._recompute_height()

    def _redraw_frame(self) -> None:
        app = get_app()
        columns = max(4, app.output.get_size().columns)
        # Draw top/bottom lines across full width
        top = "┌" + "─" * max(2, columns - 2) + "┐"
        bottom = "└" + "─" * max(2, columns - 2) + "┘"
        self.top_border.content = BufferControl(buffer=Buffer(read_only=True))
        self.bottom_border.content = BufferControl(buffer=Buffer(read_only=True))
        self.top_border.content.buffer.text = top
        self.bottom_border.content.buffer.text = bottom
        # Vertical borders
        self.left_border.content = BufferControl(buffer=Buffer(read_only=True))
        self.right_border.content = BufferControl(buffer=Buffer(read_only=True))
        height = self.input_window.height.preferred or 1
        self.left_border.content.buffer.text = "\n".join(["│" for _ in range(height)])
        self.right_border.content.buffer.text = "\n".join(["│" for _ in range(height)])
        app.invalidate()

    def _recompute_height(self) -> None:
        app = get_app()
        columns = max(10, app.output.get_size().columns)
        # inner width accounts for borders and prompt prefix
        inner_width = max(1, columns - 2 - 2)  # -2 borders, -2 for "→ " approx
        text = self.buffer.text or ""
        if not text:
            needed = 1
        else:
            needed = 0
            for line in text.splitlines() or [""]:
                wrapped: List[str] = textwrap.wrap(line, width=max(1, inner_width)) or [""]
                needed += len(wrapped)
        self.input_window.height = D(preferred=max(1, needed))
        self._redraw_frame()
        app.invalidate()

# Removed async _resize_watcher function to fix event loop issues

    def run(self) -> str | None:
        self._recompute_height()
        return self.app.run()


def _stream_agent_response(prompt_text: str) -> None:
    """Optional: example of streaming agent output using cursor-agent CLI."""
    cmd = ["cursor-agent", prompt_text, "--print", "--output-format", "stream-json"]
    try:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1) as p:
            for line in iter(p.stdout.readline, ""):
                try:
                    event = json.loads(line.strip())
                    if event.get("type") == "assistant" and "message" in event:
                        for part in event["message"].get("content", []):
                            if part.get("type") == "text":
                                sys.stdout.write(part["text"])  # non-destructive print
                                sys.stdout.flush()
                    elif event.get("type") == "result":
                        print()
                        break
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        pass


def run_interactive() -> None:
    ui = DynamicPromptUI()
    result = ui.run()
    if result is None:
        print("Ввод отменён")
        return
    if result.strip():
        print()
        _stream_agent_response(result.strip())


if __name__ == "__main__":
    run_interactive()