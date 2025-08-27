#!/usr/bin/env python3
"""
Thin wrapper to preserve the original entrypoint while delegating to
modularized UI implementation.
"""

from .interactive_runner import run_interactive



if __name__ == "__main__":
    run_interactive()