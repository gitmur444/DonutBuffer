"""
Prompt Toolkit based single-frame multi-line input UI with dynamic placeholder
and automatic height adjustment on text changes and terminal resize.
"""

from __future__ import annotations

from typing import List, Optional

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout import HSplit, Layout, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.containers import VSplit
from prompt_toolkit.layout.dimension import Dimension as D
from prompt_toolkit.layout.processors import BeforeInput
from prompt_toolkit.styles import Style

from .constants import PLACEHOLDER, DEFAULT_STYLE_DICT
from .history import MessageHistory
from .frame import TextFrame
from .keybindings import create_keybindings
from .sizing import LayoutSizer
from .resize import run_resize_watcher
from ..core.message_bus import UIEventBus


class DynamicPromptUI:
    def __init__(
        self,
        full_screen: bool = False,
        history_text: str = "",
        initial_text: str = "",
        initial_cursor: Optional[int] = None,
    ) -> None:
        self.placeholder_active = True
        self._full_screen = full_screen
        self._history_text = history_text
        self._start_cols: Optional[int] = None
        self._start_rows: Optional[int] = None
        self._history = MessageHistory(self._history_text)

        self.buffer = Buffer(multiline=True)
        self.buffer.on_text_changed += self._on_text_changed
        # Restore initial text and cursor if provided
        if initial_text:
            self.buffer.text = initial_text
            if isinstance(initial_cursor, int):
                try:
                    self.buffer.cursor_position = max(0, min(len(self.buffer.text), initial_cursor))
                except Exception:
                    pass

        self.input_window = Window(
            content=BufferControl(
                buffer=self.buffer,
                input_processors=[BeforeInput(self._before_input)],
                focusable=True,
            ),
            wrap_lines=True,
            height=D(preferred=1),
        )

        # Frame with borders
        self._frame = TextFrame()

        # History area: shows assistant/user/system messages
        self.history_window = Window(
            content=self._history.control,
            wrap_lines=True,
            dont_extend_height=True,
            height=D.exact(0),
        )

        def _on_submit() -> str:
            user_text = self.buffer.text.rstrip("\n")
            if not user_text:
                return ""
            self._append_user_message(user_text)
            self.buffer.text = ""
            self._recompute_height()
            return user_text

        self.kb = create_keybindings(_on_submit, self._apply_assistant_text)

        self.style = Style.from_dict(DEFAULT_STYLE_DICT)

        # Root layout always shows history on top; fullscreen adds filler
        if self._full_screen:
            root = HSplit([
                self.history_window,
                self._frame.top,
                VSplit([self._frame.left, self.input_window, self._frame.right]),
                self._frame.bottom,
                Window(height=D(weight=1)),
            ])
        else:
            root = HSplit([
                self.history_window,
                self._frame.top,
                VSplit([self._frame.left, self.input_window, self._frame.right]),
                self._frame.bottom,
            ])

        self.app = Application(
            layout=Layout(root),
            key_bindings=self.kb,
            mouse_support=False,
            full_screen=self._full_screen,
            style=self.style,
            refresh_interval=0.2,
        )

        # Background tasks must be created when an event loop is running.
        self._invalidate()
        UIEventBus.instance().set_consumer(self._apply_assistant_text)
        self._sizer = LayoutSizer()

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
        self._sizer.recompute(
            app=app,
            buffer=self.buffer,
            frame=self._frame,
            history=self._history,
            history_window=self.history_window,
            input_window=self.input_window,
            full_screen=self._full_screen,
        )
        self._invalidate()

    def _draw_borders(self, columns: int) -> None:
        self._frame.redraw_borders(columns)

    def _update_history_view(self, columns: int) -> None:
        self._history.update_view(columns)

    def _append_user_message(self, text: str) -> None:
        self._history.append_user(text)
        self._update_history_view(get_app().output.get_size().columns)

    def _append_assistant_chunk(self, text: str) -> None:
        self._history.append_assistant_chunk(text)
        self._update_history_view(get_app().output.get_size().columns)

    def _apply_assistant_text(self, text: str) -> None:
        def _do():
            self._append_assistant_chunk(text)
            self._recompute_height()
        get_app().call_from_executor(_do)

    async def _resize_watcher(self) -> None:
        app = self.app

        def _on_first(_c: int, _r: int) -> None:
            if self._start_cols is None or self._start_rows is None:
                s = app.output.get_size()
                self._start_cols, self._start_rows = s.columns, s.rows

        def _on_resize(_c: int, _r: int) -> None:
            if not self._full_screen:
                try:
                    cur_pos = self.buffer.cursor_position
                except Exception:
                    cur_pos = None
                app.exit(result=("__RESIZE_FULL__", self.buffer.text, cur_pos))
                return
            self._recompute_height()

        await run_resize_watcher(app, _on_first, _on_resize)

    def run(self) -> str | None:
        self._recompute_height()
        # Create the background task after the event loop is running
        def _pre_run() -> None:
            # initialize size and schedule watcher
            s = self.app.output.get_size()
            self._start_cols, self._start_rows = s.columns, s.rows
            self.app.create_background_task(self._resize_watcher())
        return self.app.run(pre_run=_pre_run)


__all__ = ["DynamicPromptUI"]

