# MCP Intent Detector

This simplified module uses a local LLM via Ollama to determine what the user
is trying to do. It prints one of four intents to the console:

- `modify_code`
- `shell_command`
- `generate_script`
- `ask_question`

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure [Ollama](https://ollama.com/) is running locally and exposes the API
   at `http://localhost:11434` with the `llama3` model available.

## Usage

Run the module with a command string:

```bash
python -m mcp "show me the ring buffer code"
```

It will print the detected intent, e.g. `ask_question`.
