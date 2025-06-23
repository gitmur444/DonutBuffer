# Local MCP Server

This FastAPI server exposes a `/command` endpoint that can interact with a local LLM via Ollama and perform tasks on a local C++ codebase.

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Ensure [Ollama](https://ollama.com/) is running locally and exposes the API at `http://localhost:11434` with the `llama3` model available.
3. (Optional) Install Docker if you want commands to run inside containers.

## Running

```bash
uvicorn mcp.main:app --reload
```

Send POST requests to `http://localhost:8000/command` with JSON body:
```json
{ "text": "your instruction" }
```

Depending on the detected intent, the server may modify `codebase/ring_buffer.cpp`, execute safe shell commands, generate scripts, or simply answer a question.

The `codebase` folder includes a small driver program that links against the
project's ring buffer implementation found under `src/ringbuffer`. Building it
via `make -C codebase` will produce a standalone example binary using the same
ring buffers as the main project.
