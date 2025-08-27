"""
Interactive runner that composes the prompt UI and agent streaming logic.
"""

from __future__ import annotations

from .prompt_ui import DynamicPromptUI
from .agent_stream import stream_agent_response


def run_interactive(preface_text: str | None = None) -> None:
    is_full_screen = False
    initial_text = ""
    initial_cursor = None

    while True:
        ui = DynamicPromptUI(
            full_screen=is_full_screen,
            history_text=(preface_text or "") if is_full_screen else "",
            initial_text=initial_text if is_full_screen else "",
            initial_cursor=initial_cursor if is_full_screen else None,
        )
        try:
            result = ui.run()
        except KeyboardInterrupt:
            print("\nВыход...")
            break

        # Handle resize-triggered fullscreen switch
        if isinstance(result, tuple) and result and result[0] == "__RESIZE_FULL__":
            is_full_screen = True
            initial_text = result[1] if len(result) > 1 and isinstance(result[1], str) else ""
            initial_cursor = result[2] if len(result) > 2 else None
            # Relaunch UI in fullscreen with restored text/cursor
            continue

        if result is None:
            print("Выход...")
            break

        user_text = (result or "").strip() if isinstance(result, str) else ""
        if not user_text:
            # Empty input — just redraw a new prompt
            continue

        print()
        stream_agent_response(user_text)
        # Loop repeats and reopens the input frame (keeping current fullscreen state)


__all__ = ["run_interactive"]

