"""
Shared constants and style configuration for the interactive UI.
"""

PLACEHOLDER: str = "Plan, search, build anything"

# prompt_toolkit style mapping used by the UI
DEFAULT_STYLE_DICT = {
    "prompt": "bold",
    "placeholder": "#888888 italic",
}

__all__ = [
    "PLACEHOLDER",
    "DEFAULT_STYLE_DICT",
]

