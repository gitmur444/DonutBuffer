#!/usr/bin/env python3
"""
Interactive CLI using prompt_toolkit with dynamic single-line frame prompt.
- Full frame visible at start
- Placeholder "→ Plan, search, build anything" in gray until typing
- Only "→" remains once user starts typing
- Auto-expands vertically as text wraps or on explicit newline
- Adjusts to terminal resize, wrapping content accordingly
"""

import asyncio
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
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.containers import VSplit
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame


PLACEHOLDER = "Plan, search, build anything"


def _build_preflight_text() -> str:
    lines = [
        "",
        "Preflight checks:",
        "  [1/5] Dependencies: OK",
        "  [2/5] GitHub token: OK",
        "  [3/5] MCP config: OK",
        "  [4/5] Integration: OK",
        "  [5/5] Ambient: OK",
        "",
        "Type below. Ctrl+J → newline, Enter → submit.",
        "",
    ]
    return "\n".join(lines)

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
            width=D(weight=1),
        )

        # Custom borders (top/bottom lines + left/right vertical bars)
        self._top_ctrl = FormattedTextControl(text="")
        self._bottom_ctrl = FormattedTextControl(text="")
        self.frame_top = Window(content=self._top_ctrl, height=D.exact(1), dont_extend_height=True)
        self.frame_bottom = Window(content=self._bottom_ctrl, height=D.exact(1), dont_extend_height=True)
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

        # Перенос строки: используйте Ctrl+J (Shift+Enter не различается в большинстве терминалов)

        @self.kb.add("enter")
        def _(event) -> None:
            event.app.exit(result=self.buffer.text)

        self.style = Style.from_dict({
            "prompt": "bold",
            "placeholder": "#888888 italic",
        })

        self.app = Application(
            layout=Layout(
                HSplit([
                    self.frame_top,
                    VSplit([self.left_border, self.input_window, self.right_border]),
                    self.frame_bottom,
                ])
            ),
            key_bindings=self.kb,
            mouse_support=False,
            full_screen=False,
            style=self.style,
            refresh_interval=0.2,
        )

        # Запускаем наблюдатель за ресайзом после старта event loop
        self.app.pre_run_callables.append(self._start_resize_watcher)
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
        size = app.output.get_size()
        columns = max(10, size.columns)
        # inner width accounts for borders and prompt prefix
        inner_width = max(1, columns - 2 - 2)  # -2 borders, -2 for "→ " approx
        text = self.buffer.text
        # count visual lines, preserving trailing empty line when text ends with \n
        lines = text.split("\n") if text != "" else [""]
        needed = 0
        for line in lines:
            wrapped: List[str] = textwrap.wrap(line, width=max(1, inner_width)) or [""]
            needed += max(1, len(wrapped))
        needed = max(1, needed)
        # set heights for input and vertical borders
        self.input_window.height = D.exact(needed)
        self.left_border.height = D.exact(needed)
        self.right_border.height = D.exact(needed)
        # redraw top/bottom borders to current width
        top = "┌" + "─" * max(2, columns - 2) + "┐"
        bottom = "└" + "─" * max(2, columns - 2) + "┘"
        self._top_ctrl.text = top
        self._bottom_ctrl.text = bottom
        self._invalidate()

    def _start_resize_watcher(self) -> None:
        # Теперь у приложения уже есть event loop
        get_app().create_background_task(self._resize_watcher())

    async def _resize_watcher(self) -> None:
        app = self.app
        last_columns = app.output.get_size().columns
        while True:
            await asyncio.sleep(0.2)
            size = app.output.get_size()
            if size.columns != last_columns:
                last_columns = size.columns
                # Пересчитываем высоту на изменение ширины (wrap меняется)
                self._recompute_height()

    def run(self) -> str | None:
        self._recompute_height()
        result = self.app.run()
        # Подсчитываем, сколько строк заняла рамка, чтобы можно было зачистить перед следующим показом
        preferred = self.input_window.height.preferred or 1
        # Frame добавляет верхнюю и нижнюю границы
        self.last_drawn_lines = max(1, preferred) + 2
        return result


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


def _run_prompt_application(full_screen: bool, initial_text: str = "", initial_cursor: int | None = None, history_text: str = ""):
    kb = KeyBindings()
    buf = Buffer(multiline=True)
    if initial_text:
        buf.text = initial_text
        if isinstance(initial_cursor, int):
            try:
                buf.cursor_position = max(0, min(len(buf.text), initial_cursor))
            except Exception:
                pass

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
        event.app.exit(result=buf.text)

    placeholder_active = {"v": len(buf.text) == 0}

    def before_input():
        if placeholder_active["v"]:
            return [("class:prompt", "→ "), ("class:placeholder", PLACEHOLDER)]
        return [("class:prompt", "→ ")]

    def on_text_changed(_):
        placeholder_active["v"] = len(buf.text) == 0
        recompute_height()

    buf.on_text_changed += on_text_changed

    input_window = Window(
        content=BufferControl(buffer=buf, input_processors=[BeforeInput(before_input)], focusable=True),
        wrap_lines=True,
        height=D(preferred=1),
        width=D(weight=1),
    )

    # History area (inside app). Fixed height exactly by content lines.
    history_ctrl = FormattedTextControl(text=history_text)
    history_window = Window(
        content=history_ctrl,
        wrap_lines=True,
        dont_extend_height=True,
        height=D.exact(0),
    )

    top_ctrl = FormattedTextControl(text="")
    bottom_ctrl = FormattedTextControl(text="")
    frame_top = Window(content=top_ctrl, height=D.exact(1), dont_extend_height=True)
    frame_bottom = Window(content=bottom_ctrl, height=D.exact(1), dont_extend_height=True)
    left_border = Window(width=1, char="│", dont_extend_height=True)
    right_border = Window(width=1, char="│", dont_extend_height=True)

    def draw_borders():
        app = get_app()
        cols = max(4, app.output.get_size().columns)
        top = "┌" + "─" * max(2, cols - 2) + "┐"
        bottom = "└" + "─" * max(2, cols - 2) + "┘"
        top_ctrl.text = top
        bottom_ctrl.text = bottom

    def recompute_height():
        app = get_app()
        size = app.output.get_size()
        cols = max(10, size.columns)
        rows = max(3, size.rows)
        inner_width = max(1, cols - 2 - 2)
        text = buf.text
        lines = text.split("\n") if text != "" else [""]
        needed = 0
        for line in lines:
            wrapped = textwrap.wrap(line, width=max(1, inner_width)) or [""]
            needed += max(1, len(wrapped))
        needed = max(1, needed)
        input_window.height = D.exact(needed)
        left_border.height = D.exact(needed)
        right_border.height = D.exact(needed)
        # history exact height (wrapped), limited to available rows
        if history_text:
            h_lines = 0
            for hl in history_text.splitlines() or [""]:
                h_lines += max(1, len(textwrap.wrap(hl, width=cols)) or 1)
            max_hist = max(0, rows - (1 + needed + 1))  # top + input + bottom
            history_window.height = D.exact(min(h_lines, max_hist))
        else:
            history_window.height = D.exact(0)
        draw_borders()
        app.invalidate()

    root = HSplit([
        history_window,
        frame_top,
        VSplit([left_border, input_window, right_border]),
        frame_bottom,
    ])
    app = Application(
        layout=Layout(root),
        key_bindings=kb,
        mouse_support=False,
        full_screen=full_screen,
        style=Style.from_dict({"prompt": "", "placeholder": "#888888 italic"}),
        refresh_interval=0.2,
    )

    start_size = {"cols": None, "rows": None}

    def init_size():
        s = app.output.get_size()
        start_size["cols"] = s.columns
        start_size["rows"] = s.rows
        recompute_height()

    async def watcher():
        init_size()
        while True:
            await asyncio.sleep(0.2)
            s = app.output.get_size()
            if not full_screen and (s.columns != start_size["cols"] or s.rows != start_size["rows"]):
                app.exit(result=("__RESIZE_FULL__", buf.text, buf.cursor_position))
                return
            recompute_height()

    def start_watcher():
        get_app().create_background_task(watcher())

    app.pre_run_callables.append(start_watcher)
    buf.text = buf.text or ""
    input_window.height = D(preferred=1)
    return app.run()


def run_interactive(history_text: str = "") -> None:
    fullscreen = False
    saved_text: str = ""
    saved_cursor: int | None = None
    while True:
        try:
            result = _run_prompt_application(fullscreen, saved_text, saved_cursor, history_text)
        except KeyboardInterrupt:
            print("Выход...")
            break

        if isinstance(result, tuple) and result and result[0] == "__RESIZE_FULL__":
            # Switch to fullscreen preserving text and cursor
            fullscreen = True
            saved_text = result[1] if len(result) > 1 else ""
            saved_cursor = result[2] if len(result) > 2 else None
            continue

        if result is None:
            print("Выход...")
            break

        user_text = (result or "").strip()
        if not user_text:
            # redraw prompt again
            saved_text = ""
            saved_cursor = None
            continue

        print()
        _stream_agent_response(user_text)
        saved_text = ""
        saved_cursor = None


if __name__ == "__main__":
    run_interactive()