# DonutBuffer: Ring Buffer Visualizer

## Requirements
- C++17 compiler (g++/clang++)
- CMake 3.10+
- GLFW
- Dear ImGui
- GLAD

## Build & Run

### Быстрый старт в Docker

```sh
docker build -t donutbuffer-test .
docker run --rm donutbuffer-test --concurrent-vs-lockfree
```

- Первый запуск собирает контейнер и проект.
- Аргументы после имени образа пробрасываются в DonutBufferApp (например, можно запускать любые эксперименты).

### Build Instructions
```bash
mkdir -p build && cd build && cmake .. && make
```

## Run
```bash
./DonutBufferApp
```

## Controls
- Set number of producers, consumers, and buffer size in the GUI
- Start/stop simulation with buttons
- View real-time buffer usage and speed metrics
- See performance history graph
