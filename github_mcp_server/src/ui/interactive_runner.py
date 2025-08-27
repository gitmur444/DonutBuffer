"""
Interactive runner that composes the prompt UI and agent streaming logic.
"""

from __future__ import annotations

from .prompt_ui import DynamicPromptUI
from .agent_stream import stream_agent_response


def run_interactive(preface_text: str | None = None) -> None:
    while True:
        ui = DynamicPromptUI()
        try:
            result = ui.run()
        except KeyboardInterrupt:
            print("\nВыход...")
            break

        if result is None:
            print("Выход...")
            break

        user_text = (result or "").strip()
        if not user_text:
            # Empty input — just redraw a new prompt
            continue

        print()
        # If provided, print preface text once before streaming the agent response
        if preface_text:
            print(preface_text)
            preface_text = None
        stream_agent_response(user_text)
        # Loop repeats and reopens the input frame


__all__ = ["run_interactive"]

