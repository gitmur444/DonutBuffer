# Используем официальный образ cchh/ubuntu-cpp:22.04 как базу (есть clang, cmake, make, g++, python)
FROM ubuntu:22.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    cmake \
    clang \
    git \
    libglfw3-dev \
    libx11-dev \
    libxi-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем весь проект внутрь контейнера
WORKDIR /app
COPY . .

# Install Python requirements if present
RUN if [ -f mcp/requirements.txt ]; then \
        pip3 install --no-cache-dir -r mcp/requirements.txt; \
    fi

# Install Ollama and pull llama3 model
RUN curl -fsSL https://ollama.ai/install.sh | sh && \
    ollama pull llama3 || true

# Собираем проект через CMake
RUN mkdir -p build && cd build && cmake .. && make -j$(nproc)

# Указываем рабочую директорию для запуска
WORKDIR /app/build

# По умолчанию запускать help
ENTRYPOINT ["./DonutBufferApp"]
