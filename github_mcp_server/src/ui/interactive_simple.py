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


def _stream_agent_response_iter(prompt_text: str):
    """Yield agent output chunks incrementally (no direct printing)."""
    cmd = ["cursor-agent", prompt_text, "--print", "--output-format", "stream-json"]
    try:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1) as p:
            for line in iter(p.stdout.readline, ""):
                try:
                    event = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                if event.get("type") == "assistant" and "message" in event:
                    for part in event["message"].get("content", []):
                        if part.get("type") == "text":
                            yield part["text"]
                elif event.get("type") == "result":
                    break
    except FileNotFoundError:
        return


def _run_prompt_application(full_screen: bool, initial_text: str = "", initial_cursor: int | None = None, history_text: str = "", transcript_entries: list[list[str, str]] | None = None, stream_prompt: str | None = None, show_welcome: bool = False):
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

    # History area (preflight only). Fixed height by computed lines.
    history_ctrl = FormattedTextControl(text=history_text)
    history_window = Window(
        content=history_ctrl,
        wrap_lines=True,
        dont_extend_height=True,
        height=D.exact(0),
    )

    # Transcript area (conversation). Always below welcome and status, above input.
    transcript_ctrl = FormattedTextControl(text="")
    transcript_window = Window(
        content=transcript_ctrl,
        wrap_lines=True,
        dont_extend_height=True,
        height=D.exact(0),
    )

    # Header (fullscreen) — одна строка без рамки
    header_ctrl = FormattedTextControl(text="DonutBuffer AI Wizard - Магический помощник разработчика")
    header_window = Window(content=header_ctrl, height=D.exact(1), dont_extend_height=True)

    # Рамка приветствия Cursor Agent — статичная рамка поверх ввода
    welcome_text = (
        "⬢ Welcome to Cursor Agent Beta\n\n"
        "Cursor Agent CLI is in beta. Security safeguards are still evolving. It can read, modify, and\n"
        "delete files, and execute shell commands you approve. Use at your own risk and only in\n"
        "trusted environments.\n\n"
        "Please read about our security at https://cursor.com/security."
    )
    welcome_ctrl = FormattedTextControl(text=welcome_text)
    welcome_content = Window(content=welcome_ctrl, wrap_lines=True, dont_extend_height=True, height=D.exact(0))
    welcome_top_ctrl = FormattedTextControl(text="")
    welcome_bottom_ctrl = FormattedTextControl(text="")
    welcome_top = Window(content=welcome_top_ctrl, height=D.exact(1), dont_extend_height=True)
    welcome_bottom = Window(content=welcome_bottom_ctrl, height=D.exact(1), dont_extend_height=True)
    welcome_left = Window(width=1, char="│", dont_extend_height=True)
    welcome_right = Window(width=1, char="│", dont_extend_height=True)

    # Два пустых ряда + две статусные строки + ещё пустой ряд
    spacer_after_welcome = Window(height=D.exact(2), dont_extend_height=True)
    status1_window = Window(content=FormattedTextControl(text="Cursor Agent"), height=D.exact(1), dont_extend_height=True)
    _cwd = os.getcwd()
    _home = os.path.expanduser("~")
    _rel = _cwd.replace(_home + "/", "~/") if _cwd.startswith(_home) else _cwd
    status2_window = Window(content=FormattedTextControl(text=f"{_rel} · main"), height=D.exact(1), dont_extend_height=True)
    spacer_before_input = Window(height=D.exact(1), dont_extend_height=True)

    # (duplicate definitions removed — welcome/header already defined above)

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
        welcome_top_ctrl.text = top
        welcome_bottom_ctrl.text = bottom

    def _build_user_box(text: str, cols: int) -> str:
        inner = max(1, cols - 2)
        lines = text.split("\n") if text != "" else [""]
        wrapped_lines: list[str] = []
        for ln in lines:
            parts = textwrap.wrap(ln, width=inner) or [""]
            wrapped_lines.extend(parts)
        top = "┌" + "─" * inner + "┐"
        bottom = "└" + "─" * inner + "┘"
        body = []
        for wl in wrapped_lines:
            pad = " " * max(0, inner - len(wl))
            body.append("│" + wl + pad + "│")
        return "\n".join([top, *body, bottom])

    def _render_transcript(cols: int) -> tuple[list[str], int]:
        if not transcript_entries:
            return [], 0
        visual_lines: list[str] = []
        gap = [""]  # blank line between blocks
        first = True
        for role, txt in transcript_entries:
            if not first:
                visual_lines.extend(gap)
            first = False
            if role == "user":
                box_text = _build_user_box(txt, cols)
                visual_lines.extend(box_text.splitlines() or [""])
            else:
                # agent block: preserve newlines and indentation exactly; UI will wrap visually
                plain_lines = (txt or "").splitlines() or [""]
                visual_lines.extend(plain_lines)
        # count visual rows accounting for wrapping width
        total = 0
        for ln in visual_lines or [""]:
            total += max(1, len(textwrap.wrap(ln, width=max(1, cols))) or 1)
        return visual_lines, total

    # No manual scrolling; always stick to the newest messages

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
        # welcome box height (shown only once when show_welcome=True)
        if show_welcome:
            w_lines = 0
            for wl in welcome_text.splitlines() or [""]:
                wrapped = textwrap.wrap(wl, width=max(1, cols - 2)) or [""]
                w_lines += max(1, len(wrapped))
            welcome_content.height = D.exact(w_lines)
            welcome_left.height = D.exact(w_lines)
            welcome_right.height = D.exact(w_lines)
        else:
            w_lines = 0
            welcome_content.height = D.exact(0)
            welcome_left.height = D.exact(0)
            welcome_right.height = D.exact(0)
        # render transcript to current width and measure
        all_t_lines, t_lines = _render_transcript(cols)
        h_lines = 0
        if history_text:
            for hl in history_text.splitlines() or [""]:
                h_lines += max(1, len(textwrap.wrap(hl, width=cols)) or 1)

        # reserved rows below transcript/history stack:
        # header(optional) + welcome frame(2) + welcome content(w_lines) + spacer_after_welcome(2) + status(2)
        # + transcript_window(take_first) + spacer_before_input(1) + input frame(2) + input content(needed)
        reserved_fixed = 2 + 2 + 1 + 2 + needed
        if show_welcome:
            reserved_fixed += 2 + w_lines
        if full_screen:
            reserved_fixed += 1
        available_for_scroll = max(0, rows - reserved_fixed)

        # Allocate to transcript first (to keep recent conversation visible), then remaining for history
        # ensure at least one transcript line is visible (steal from history if needed)
        if available_for_scroll <= 0 and t_lines > 0:
            t_show = 1
            h_show = 0
        else:
            t_show = min(t_lines, available_for_scroll)
            h_show = min(h_lines, max(0, available_for_scroll - t_show))
        # keep only the last t_show lines so newest messages are visible
        if t_show > 0 and all_t_lines:
            transcript_ctrl.text = "\n".join(all_t_lines[-t_show:])
        else:
            transcript_ctrl.text = ""
        transcript_window.height = D.exact(t_show)
        history_window.height = D.exact(h_show)
        draw_borders()
        app.invalidate()

    # Manual scrolling removed per requirements

    common_stack = [history_window]
    if show_welcome:
        common_stack.extend([
            welcome_top,
            VSplit([welcome_left, welcome_content, welcome_right]),
            welcome_bottom,
        ])
    common_stack.extend([
        spacer_after_welcome,
        status1_window,
        status2_window,
        transcript_window,
        spacer_before_input,
        frame_top,
        VSplit([left_border, input_window, right_border]),
        frame_bottom,
    ])

    if full_screen:
        root = HSplit([header_window, *common_stack])
    else:
        root = HSplit(common_stack)
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

    async def stream_runner():
        # Stream agent chunks and update transcript live
        if not stream_prompt:
            return
        # Append placeholder agent entry
        if transcript_entries is not None:
            transcript_entries.append(["agent", ""])
        loop = asyncio.get_running_loop()
        def iterator():
            for chunk in _stream_agent_response_iter(stream_prompt):
                yield chunk
        # Run blocking generator in thread
        def run_and_update():
            for chunk in iterator():
                if transcript_entries is not None and transcript_entries:
                    transcript_entries[-1][1] += chunk
                # always stick to bottom; no manual scroll state kept
                try:
                    get_app().invalidate()
                except Exception:
                    pass
            # exit when done
            try:
                get_app().exit(result="__STREAM_DONE__")
            except Exception:
                pass
        await loop.run_in_executor(None, run_and_update)

    def start_watcher():
        get_app().create_background_task(watcher())
        if stream_prompt:
            get_app().create_background_task(stream_runner())

    app.pre_run_callables.append(start_watcher)
    buf.text = buf.text or ""
    input_window.height = D(preferred=1)
    return app.run()


def run_interactive(history_text: str = "") -> None:
    fullscreen = False
    saved_text: str = ""
    saved_cursor: int | None = None
    # Reset input each turn: boxes start with placeholder only
    last_submitted_len: int = 0
    # Accumulated conversation transcript (agent replies), persists across modes and prompts
    transcript_parts: list[str] = []
    # Show welcome box only once (before "Cursor Agent" line)
    welcome_shown = False
    while True:
        try:
            # Build visible history: preflight + transcript
            # We pass transcript entries to render user boxes persistently
            transcript_entries = transcript_parts
            # Ensure cursor defaults to end of current saved_text
            init_cursor = len(saved_text) if saved_cursor is None else saved_cursor
            # stream_prompt=None when just editing; set to user text after submission
            show_welcome = not welcome_shown
            result = _run_prompt_application(fullscreen, saved_text, init_cursor, history_text, transcript_entries, None, show_welcome)
            if show_welcome:
                welcome_shown = True
        except KeyboardInterrupt:
            print("Выход...")
            break

        if isinstance(result, tuple) and result and result[0] == "__RESIZE_FULL__":
            # Switch to fullscreen preserving text and cursor
            fullscreen = True
            saved_text = result[1] if len(result) > 1 else ""
            saved_cursor = result[2] if len(result) > 2 else None
            # Clamp last_submitted_len to current buffer size
            last_submitted_len = min(last_submitted_len, len(saved_text))
            continue

        if result is None:
            print("Выход...")
            break
            
        user_text_raw = result or ""
        # Detect only the newly appended part after the last submission
        if last_submitted_len > len(user_text_raw):
            # Safety: reset if buffer shrank
            last_submitted_len = 0
        new_segment = user_text_raw[last_submitted_len:]
        user_text = new_segment.strip()
        if not user_text:
            # keep box as-is if nothing new typed
            saved_text = user_text_raw
            saved_cursor = len(saved_text)
            continue

        print()
        # Record user block and then stream agent live in UI
        transcript_parts.append(["user", user_text])
        # Run UI in streaming mode to display incremental agent output
        _ = _run_prompt_application(True, "", None, history_text, transcript_parts, user_text, False)
        # Reset input box to placeholder for next turn
        saved_text = ""
        saved_cursor = None
        last_submitted_len = 0


if __name__ == "__main__":
    run_interactive()