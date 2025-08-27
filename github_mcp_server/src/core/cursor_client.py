"""
Central CursorAgent client that manages a single logical conversation session
with cursor-agent and provides streaming APIs with callbacks.

This client avoids duplicating cursor-agent process spawning logic across
modules and ensures all prompts go into the same conversation via `resume`.

Note: Because cursor-agent CLI does not expose a documented persistent stdin
interface, we maintain session continuity via `cursor-agent resume` after the
first successful prompt. If a true persistent mode becomes available, the
implementation can be swapped here without touching UI or ambient layers.
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Optional, Callable, Any


OnText = Callable[[str], None]


class CursorAgentClient:
    def __init__(self) -> None:
        self._session_id: Optional[str] = None

    def available(self) -> bool:
        try:
            result = subprocess.run(
                ["cursor-agent", "--help"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def send_stream(
        self,
        prompt: str,
        on_user: Optional[OnText] = None,
        on_chunk: Optional[OnText] = None,
        on_result: Optional[OnText] = None,
    ) -> bool:
        """Send a prompt and stream the assistant response.

        - The first call uses a fresh conversation.
        - Subsequent calls use `resume` to keep context.
        """
        cmd = (
            ["cursor-agent", prompt, "--print", "--output-format", "stream-json"]
            if not self._session_id
            else [
                "cursor-agent",
                "--resume",
                self._session_id,
                prompt,
                "--print",
                "--output-format",
                "stream-json",
            ]
        )
        try:
            with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            ) as proc:
                assert proc.stdout is not None
                printed_user = False
                for line in proc.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    obj: Any
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue

                    # Capture/verify session id
                    event_sid = obj.get("session_id") if isinstance(obj, dict) else None
                    if self._session_id is None and event_sid:
                        self._session_id = event_sid
                    if self._session_id is not None and event_sid and event_sid != self._session_id:
                        # Ignore events from other sessions
                        continue

                    if not printed_user and _is_user_event(obj):
                        content = _extract_text(obj)
                        if content and on_user:
                            on_user(content)
                        printed_user = True
                        continue

                    if _is_assistant_event(obj):
                        chunk = _extract_text(obj)
                        if chunk and on_chunk:
                            on_chunk(chunk)
                        continue

                    if isinstance(obj, dict) and obj.get("type") == "result":
                        if on_result:
                            on_result(obj.get("result") or "")
                        continue

                ok = proc.wait() == 0
                return ok
        except Exception:
            return False


def _extract_text(obj: Any) -> str:
    if isinstance(obj, dict):
        if isinstance(obj.get("message"), dict):
            return _extract_text(obj["message"])
        if isinstance(obj.get("content"), str):
            return obj.get("content")
        if isinstance(obj.get("content"), list):
            parts = []
            for it in obj.get("content"):
                t = _extract_text(it)
                if t:
                    parts.append(t)
            return "".join(parts)
        for key in ("text", "message", "data"):
            v = obj.get(key)
            t = _extract_text(v)
            if t:
                return t
    elif isinstance(obj, list):
        parts = [_extract_text(it) for it in obj]
        parts = [p for p in parts if p]
        return "\n".join(parts)
    elif isinstance(obj, str):
        return obj
    return ""


def _is_user_event(obj: Any) -> bool:
    if isinstance(obj, dict):
        if obj.get("type") == "user":
            return True
        msg = obj.get("message")
        if isinstance(msg, dict) and msg.get("role") == "user":
            return True
    return False


def _is_assistant_event(obj: Any) -> bool:
    if isinstance(obj, dict):
        if obj.get("type") == "assistant":
            return True
        msg = obj.get("message")
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            return True
    return False


_GLOBAL_CLIENT: Optional[CursorAgentClient] = None


def get_global_cursor_client() -> CursorAgentClient:
    global _GLOBAL_CLIENT
    if _GLOBAL_CLIENT is None:
        _GLOBAL_CLIENT = CursorAgentClient()
    return _GLOBAL_CLIENT


__all__ = ["CursorAgentClient", "get_global_cursor_client"]


