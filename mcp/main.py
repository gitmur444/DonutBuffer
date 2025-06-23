"""Command-line tool to detect user intent using a local LLM."""

import argparse

from .llm import detect_intent


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect intent of a command")
    parser.add_argument("text", help="User command text")
    args = parser.parse_args()
    intent = detect_intent(args.text)
    print(intent)


if __name__ == "__main__":
    main()
