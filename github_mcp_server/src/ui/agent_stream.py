"""
Utilities for streaming agent responses from the `cursor-agent` CLI.
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Iterable, Optional


def stream_agent_response(prompt_text: str) -> None:
    """Stream assistant output produced by `cursor-agent` for the given prompt.

    This function is resilient to the CLI being unavailable (no exception raised).
    """
    cmd = [
        "cursor-agent",
        prompt_text,
        "--print",
        "--output-format",
        "stream-json",
    ]
    try:
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        ) as process:
            assert process.stdout is not None
            for line in iter(process.stdout.readline, ""):
                try:
                    event = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue

                if event.get("type") == "assistant" and "message" in event:
                    for part in event["message"].get("content", []):
                        if part.get("type") == "text":
                            sys.stdout.write(part["text"])
                            sys.stdout.flush()
                elif event.get("type") == "result":
                    print()
                    break
    except FileNotFoundError:
        # cursor-agent not installed; silently ignore
        return


__all__ = ["stream_agent_response"]

