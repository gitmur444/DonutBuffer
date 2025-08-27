"""
UI-facing convenience function that delegates streaming to the central
CursorAgentClient, avoiding per-call process spawning and preserving context.
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Iterable, Optional
from ..core.cursor_client import get_global_cursor_client


def stream_agent_response(prompt_text: str) -> None:
    client = get_global_cursor_client()
    def on_chunk(t: str) -> None:
        sys.stdout.write(t)
        sys.stdout.flush()
    def on_result(_t: str) -> None:
        print()
    client.send_stream(prompt_text, on_chunk=on_chunk, on_result=on_result)


__all__ = ["stream_agent_response"]

