# DonutBuffer: Ring Buffer Visualizer

## Requirements
- C++20 compiler (g++/clang++, with module support)
- CMake 3.28+ (recommended for best module support, current version after update: 4.0.3)
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

- The first run builds the container and the project.
- Arguments after the image name are passed to `DonutBufferApp` (e.g., to run any experiment).

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
