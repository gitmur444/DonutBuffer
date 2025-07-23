# DonutBuffer: Ring Buffer Visualizer

## Project Build

```sh
make
```
- Build is performed from the project root. Makefile automatically creates the build folder, calls cmake and builds the project.
- To clean the build use:
```sh
make clean
```

## Running the Application

On macOS the binary is located inside .app:
```sh
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp [options]
```

## Smart GTest System

The project includes an integrated Smart GTest system with PostgreSQL logging:

```sh
# Quick start Smart GTest
cd tests/smart_gtest
./quick_start.sh

# Manual test execution
make build
./build/test_example

# CLI database management
./build/smart_test_cli status
./build/smart_test_cli recent
```

For more details see `tests/smart_gtest/README.md`

## Examples of running with parameters:
```sh
# Example: mutex buffer, 3 producers, 2 consumers, 8 MB buffer, 32 MB data
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp --buffer-type mutex --producers 3 --consumers 2 --buffer-size_mb 8 --total-transfer_mb 32

# Example: lockfree buffer, 1 producer, 1 consumer, 4 MB buffer, 16 MB data
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp --buffer-type lockfree --producers 1 --consumers 1 --buffer-size_mb 4 --total-transfer_mb 16

# Example: concurrent_queue, run without GUI
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp --nogui --buffer-type concurrent_queue --producers 2 --consumers 2 --buffer-size_mb 2 --total-transfer_mb 8
```
## Command Line Options

### C++ Entry Point (`DonutBufferApp`)
- `--nogui` &mdash; run without graphical interface. Default value is `true`.
- `--mutex-vs-lockfree` &mdash; execute comparison test between `MutexRingBuffer` and `LockFreeRingBuffer` and exit.
- `--concurrent-vs-lockfree` &mdash; execute test of `ConcurrentQueue` against `LockFreeRingBuffer` and exit.
- `--buffer-type {lockfree, mutex, concurrent_queue}` &mdash; type of buffer used.
- `--producers N` &mdash; number of producer threads.
- `--consumers N` &mdash; number of consumer threads.
- `--buffer-size_mb N` &mdash; buffer size in megabytes.
- `--total-transfer_mb N` &mdash; total amount of data transferred through the ring buffer in megabytes.

### Python Entry Point (`python -m mcp`)
- `text` &mdash; required user command text.
- `--full-response` &mdash; output full information instead of just intent.
- `--provider {ollama, openai}` &mdash; LLM provider (default from `LLM_PROVIDER` variable or `ollama`).
- `--openai-key KEY` &mdash; OpenAI API key (default from `OPENAI_API_KEY` variable).
- `--model MODEL` &mdash; model for selected provider (default from `OLLAMA_MODEL` or `OPENAI_MODEL`).

### Environment Variables
- `LLM_PROVIDER` &mdash; default LLM provider (`ollama` if not set).
- `OPENAI_API_KEY` &mdash; API key for OpenAI.
- `OPENAI_MODEL` &mdash; model for OpenAI (`gpt-3.5-turbo` by default).
- `OLLAMA_MODEL` &mdash; model for Ollama (`llama3` by default).


## Multi-Provider Command Interface

The repository includes a simple command-line tool located in the `mcp` folder.
It can work with either a local Ollama model or the OpenAI API. Below are common
usage patterns.

### Using OpenAI (key in command line)
```bash
python -m mcp --provider openai --openai-key YOUR_API_KEY "your request" --full-response
```

### Using OpenAI (key from environment variable)
```bash
export OPENAI_API_KEY=YOUR_API_KEY
python -m mcp --provider openai "your request" --full-response
```

### Using Ollama (default)
```bash
python -m mcp "your request" --full-response
```

### Selecting specific model
```bash
python -m mcp --provider openai --model gpt-4 "your request" --full-response
python -m mcp --provider ollama --model codellama "your request" --full-response
```

