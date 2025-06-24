# DonutBuffer: Ring Buffer Visualizer

## Requirements
- C++20 compiler (g++/clang++, with module support)
- CMake 3.28+ (recommended for best module support, current version after update: 3.28.3)
- Ninja (for building with C++20 modules via CMake)
- GLFW
- Dear ImGui
- GLAD

## Build & Run

### Quick Start with Docker
(Note: Dockerfile may need updates for C++20 module builds)

```sh
docker build -t donutbuffer-test .
docker run --rm donutbuffer-test --concurrent-vs-lockfree
```

The Docker image now installs Python requirements from `mcp/requirements.txt` and sets up Ollama with the `llama3` model. If `mcp/requirements.txt` is missing, the step is skipped.

- The first run builds the container and the project.
- Arguments after the image name are passed to `DonutBufferApp` (e.g., to run any experiment).

### Quick Start with Codespaces
This repository includes a [dev container](https://containers.dev/) configuration. If you open it in GitHub Codespaces (or any editor supporting dev containers), the environment will be prepared automatically:

```bash
./build/DonutBufferApp
```

### Build Instructions (Local)
```bash
# Ensure Ninja is installed (e.g., brew install ninja)
mkdir -p build
cd build
cmake .. -G Ninja # Specify Ninja as the generator
cmake --build .  # Run the build through CMake (which will invoke Ninja)
# or directly: ninja
```

## Run
From the `build` directory:
```bash
./DonutBufferApp
```
Or, if you are in the project's root directory:
```bash
./build/DonutBufferApp
```

## Controls
- Set the number of producers, consumers, and buffer size in the GUI.
- Start/stop the simulation using the buttons.
- View real-time buffer usage and speed metrics.
- See the performance history graph.

## Multi-Provider Command Interface

The repository includes a simple command-line tool located in the `mcp` folder.
It can work with either a local Ollama model or the OpenAI API. Below are common
usage patterns.

### Использование OpenAI (ключ в командной строке)
```bash
python -m mcp --provider openai --openai-key YOUR_API_KEY "ваш запрос" --full-response
```

### Использование OpenAI (ключ из переменной окружения)
```bash
export OPENAI_API_KEY=YOUR_API_KEY
python -m mcp --provider openai "ваш запрос" --full-response
```

### Использование Ollama (по умолчанию)
```bash
python -m mcp "ваш запрос" --full-response
```

### Выбор конкретной модели
```bash
python -m mcp --provider openai --model gpt-4 "ваш запрос" --full-response
python -m mcp --provider ollama --model codellama "ваш запрос" --full-response
```
