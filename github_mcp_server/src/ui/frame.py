from __future__ import annotations

from prompt_toolkit.layout import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension as D


class TextFrame:
    """Текстовые рамки вокруг ввода: верх/низ и вертикальные бордеры.
    Обновляет размеры по мере изменения высоты инпута."""

    def __init__(self) -> None:
        self.top_ctrl = FormattedTextControl(text="")
        self.bottom_ctrl = FormattedTextControl(text="")
        self.top = Window(content=self.top_ctrl, height=D.exact(1), dont_extend_height=True)
        self.bottom = Window(content=self.bottom_ctrl, height=D.exact(1), dont_extend_height=True)
        self.left = Window(width=1, char="│", dont_extend_height=True)
        self.right = Window(width=1, char="│", dont_extend_height=True)

    def set_input_height(self, height_lines: int) -> None:
        self.left.height = D.exact(height_lines)
        self.right.height = D.exact(height_lines)

    def redraw_borders(self, columns: int) -> None:
        cols = max(4, columns)
        top = "┌" + "─" * max(2, cols - 2) + "┐"
        bottom = "└" + "─" * max(2, cols - 2) + "┘"
        self.top_ctrl.text = top
        self.bottom_ctrl.text = bottom


__all__ = ["TextFrame"]


