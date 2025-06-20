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
    && rm -rf /var/lib/apt/lists/*

# Копируем весь проект внутрь контейнера
WORKDIR /app
COPY . .

# Собираем проект через CMake
RUN mkdir -p build && cd build && cmake .. && make -j$(nproc)

# Указываем рабочую директорию для запуска
WORKDIR /app/build

# По умолчанию запускать help
ENTRYPOINT ["./DonutBufferApp"]
