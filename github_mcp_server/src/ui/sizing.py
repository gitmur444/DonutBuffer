from __future__ import annotations

import textwrap
from prompt_toolkit.layout import Window
from prompt_toolkit.layout.dimension import Dimension as D
from .frame import TextFrame
from .history import MessageHistory


class LayoutSizer:
    """Пересчёт высот инпута/истории и перерисовка рамок."""

    def _calc_input_height(self, text: str, columns: int) -> int:
        columns = max(10, columns)
        inner_width = max(1, columns - 4)  # 2 бордера + «→ »
        lines = text.split("\n") if text != "" else [""]
        needed = 0
        for line in lines:
            wraps = textwrap.wrap(line, width=inner_width) or [""]
            needed += max(1, len(wraps))
        return max(1, needed)

    def _calc_history_lines(self, history: MessageHistory, columns: int) -> int:
        history.update_view(columns)
        return history.rendered_lines_count(columns)

    def recompute(
        self,
        app,
        buffer,
        frame: TextFrame,
        history: MessageHistory,
        history_window: Window,
        input_window: Window,
        full_screen: bool,
    ) -> None:
        size = app.output.get_size()
        columns = max(10, size.columns)

        # Input height and borders
        box_height = self._calc_input_height(buffer.text, columns)
        input_window.height = D.exact(box_height)
        frame.set_input_height(box_height)

        # History height
        rows = max(3, size.rows)
        h_lines = self._calc_history_lines(history, columns)
        max_hist = max(0, rows - (3 + box_height))
        history_window.height = D.exact(min(h_lines, max_hist))

        # Borders
        frame.redraw_borders(columns)


__all__ = ["LayoutSizer"]


