# Ring Buffer GUI

Interactive multithreaded ring buffer visualization with Dear ImGui and OpenGL.

## Features

- Real-time visualization of producer-consumer pattern with a ring buffer
- Configurable number of producers and consumers
- Performance monitoring with real-time speedometer
- Historical performance visualization with persistent graph
- Thread-safe implementation with mutex and condition variables

## Dependencies

- GLFW
- Dear ImGui
- GLAD (OpenGL loader)
- C++17 standard library

## Building

```bash
# Create build directory
mkdir -p build
cd build

# Configure and build
cmake ..
make
```

## Usage

- Adjust producer and consumer counts, buffer size
- Start/stop simulation
- Monitor buffer usage and processing speeds
- Compare performance across different runs using the graph
