"""
Minimal PTY bridge to run cursor-agent and inject messages via FIFO.

- Spawns `cursor-agent` under a pseudo-terminal so the user can interact.
- Creates and listens on `~/.cursor/inbox` named pipe.
- Any line written to the FIFO is forwarded to the agent as if typed by the user.
"""

import os
import signal
import shutil
import struct
import fcntl
import termios
import threading
import time
from pathlib import Path

import pexpect


class PTYBridge:
    """Runs `cursor-agent` in a PTY and forwards FIFO input to it."""

    def __init__(self, fifo_path: Path | None = None):
        self.fifo_path = fifo_path or (Path.home() / ".cursor" / "inbox")
        self._stop = False
        self.child = None
        self._interact_done = False

    def _ensure_fifo(self) -> None:
        fifo_dir = self.fifo_path.parent
        fifo_dir.mkdir(parents=True, exist_ok=True)
        if self.fifo_path.exists():
            # If exists but is a regular file, remove and recreate as FIFO
            if not self.fifo_path.is_fifo():
                try:
                    self.fifo_path.unlink()
                except Exception:
                    pass
        if not self.fifo_path.exists():
            os.mkfifo(self.fifo_path, 0o600)

    def _user_interact(self) -> None:
        try:
            if self.child is not None:
                # Ctrl-] (ASCII 29) to exit bridge cleanly
                self.child.interact(escape_character=chr(29))
        except Exception:
            pass
        finally:
            # User requested to exit interaction
            self._interact_done = True
            self._request_stop()

    def _fifo_loop(self) -> None:
        # Open the FIFO repeatedly to handle writer close/open cycles
        while not self._stop and self.child is not None and self.child.isalive():
            try:
                with open(self.fifo_path, "r", encoding="utf-8", errors="ignore") as fifo:
                    for line in fifo:
                        if self._stop or self.child is None or not self.child.isalive():
                            return
                        text = line.rstrip("\n")
                        if text:
                            # Special control command to stop bridge
                            if text.strip() in {"::exit", "::quit", "::stop"}:
                                self._request_stop()
                                return
                            try:
                                self.child.sendline(text)
                            except Exception:
                                # Best-effort; continue listening
                                pass
            except FileNotFoundError:
                # FIFO removed externally; recreate and continue
                try:
                    self._ensure_fifo()
                except Exception:
                    time.sleep(0.5)
            except Exception:
                # Back off briefly on unexpected errors
                time.sleep(0.2)

    def run(self) -> int:
        """Run the PTY bridge. Returns the cursor-agent exit status."""
        self._ensure_fifo()

        try:
            # Spawn cursor-agent with a PTY; inherit environment and terminal
            # echo=False ensures Ctrl+C is delivered to child; we still trap it to exit
            self.child = pexpect.spawn(
                "cursor-agent",
                encoding="utf-8",
                timeout=None
            )
        except Exception as e:
            print(f"❌ Failed to start cursor-agent in PTY: {e}")
            return 1

        # Sync initial window size so TUI renders correctly
        try:
            self._sync_winsize()
        except Exception:
            pass

        # Forward SIGINT/SIGTERM to child AND exit bridge immediately
        def _sig_handler(signum, frame):
            try:
                if self.child is not None and self.child.isalive():
                    # Send SIGINT directly to the child process group
                    os.kill(self.child.pid, signal.SIGINT)
            except Exception:
                pass
            # Stop bridge right away so user returns to shell
            self._request_stop()
        try:
            signal.signal(signal.SIGINT, _sig_handler)
            signal.signal(signal.SIGTERM, _sig_handler)
        except Exception:
            pass

        # Propagate terminal resize to child
        def _sigwinch(signum, frame):
            try:
                self._sync_winsize()
            except Exception:
                pass
        try:
            signal.signal(signal.SIGWINCH, _sigwinch)
        except Exception:
            pass

        # Start user interaction on a dedicated thread
        t_user = threading.Thread(target=self._user_interact, daemon=True)
        t_user.start()

        # Start FIFO listener on another thread
        t_fifo = threading.Thread(target=self._fifo_loop, daemon=True)
        t_fifo.start()

        # Wait for the agent to exit
        # Wait for the agent to exit OR for stop request (e.g., Ctrl+C)
        while not self._stop and self.child is not None and self.child.isalive():
            try:
                self.child.wait(timeout=0.2)
            except Exception:
                # Ignore timeouts; loop until stop
                pass
        self._stop = True

        # Return exit status if available
        try:
            return self.child.exitstatus if self.child is not None else 0
        except Exception:
            return 0

    def _request_stop(self) -> None:
        if self._stop:
            return
        self._stop = True
        try:
            if self.child is not None and self.child.isalive():
                # Try graceful interruption
                try:
                    self.child.sendcontrol('c')
                except Exception:
                    pass
                # Give it a moment
                try:
                    self.child.expect(pexpect.EOF, timeout=1)
                except Exception:
                    pass
                # Ensure termination
                try:
                    self.child.terminate(force=True)
                except Exception:
                    pass
        finally:
            self.child = None

    def _sync_winsize(self) -> None:
        """Sync current terminal window size to the child PTY."""
        if self.child is None:
            return
        try:
            # Prefer ioctl to get exact size
            buf = fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0))
            rows, cols, _, _ = struct.unpack('HHHH', buf)
            if rows == 0 or cols == 0:
                sz = shutil.get_terminal_size(fallback=(80, 24))
                cols, rows = sz.columns, sz.lines
        except Exception:
            sz = shutil.get_terminal_size(fallback=(80, 24))
            cols, rows = sz.columns, sz.lines
        try:
            self.child.setwinsize(rows, cols)
        except Exception:
            pass


def run_bridge() -> int:
    return PTYBridge().run()


if __name__ == "__main__":
    raise SystemExit(run_bridge())


