import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import List

CODEBASE_PATH = Path(__file__).resolve().parent.parent / "codebase"

WHITELIST = {"ls", "cat", "echo", "make", "python3", "bash"}


def apply_patch_and_build(patch_text: str) -> str:
    """Apply a unified diff patch to ring_buffer.cpp and run make."""
    patch_file = tempfile.NamedTemporaryFile("w", delete=False)
    patch_file.write(patch_text)
    patch_file.close()
    result = []
    try:
        # Apply patch
        proc = subprocess.run(
            ["patch", "-p0", f"-i{patch_file.name}"],
            cwd=CODEBASE_PATH,
            capture_output=True,
            text=True,
        )
        result.append(proc.stdout + proc.stderr)
        # Build
        proc = subprocess.run(
            ["make"], cwd=CODEBASE_PATH, capture_output=True, text=True
        )
        result.append(proc.stdout + proc.stderr)
    finally:
        os.unlink(patch_file.name)
    return "\n".join(result)


def run_shell_command(command: str) -> str:
    """Run a shell command if it's in the whitelist."""
    parts = shlex.split(command)
    if not parts or parts[0] not in WHITELIST:
        return "Command not allowed"
    proc = subprocess.run(parts, capture_output=True, text=True)
    return proc.stdout + proc.stderr


def save_and_maybe_run_script(info: dict) -> str:
    """Save generated script to file and run if requested."""
    filename = info.get("filename", "script.sh")
    content = info.get("content", "")
    run = info.get("run", False)
    filepath = CODEBASE_PATH / filename
    filepath.write_text(content)
    if run:
        if filename.endswith(".py"):
            cmd = ["python3", str(filepath)]
        else:
            cmd = ["bash", str(filepath)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        return proc.stdout + proc.stderr
    return f"Script saved to {filepath}"
