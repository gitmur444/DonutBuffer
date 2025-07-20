# DonutBuffer: Ring Buffer Visualizer

## Сборка проекта

```sh
make
```
- Сборка выполняется из корня проекта. Makefile автоматически создаёт папку build, вызывает cmake и собирает проект.
- Для очистки сборки используйте:
```sh
make clean
```

## Запуск приложения

На macOS бинарник находится внутри .app:
```sh
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp [опции]
```

## Smart GTest система

В проекте доступна интегрированная система Smart GTest с PostgreSQL логированием:

```sh
# Быстрый старт Smart GTest
cd tests/smart_gtest
./quick_start.sh

# Ручной запуск тестов
make build
./build/test_example

# CLI управление базой данных
./build/smart_test_cli status
./build/smart_test_cli recent
```

Подробнее см. `tests/smart_gtest/README.md`

## Примеры запуска с параметрами:
```sh
# Пример: mutex-буфер, 3 производителя, 2 потребителя, 8 МБ буфер, 32 МБ данных
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp --buffer-type mutex --producers 3 --consumers 2 --buffer-size_mb 8 --total-transfer_mb 32

# Пример: lockfree-буфер, 1 производитель, 1 потребитель, 4 МБ буфер, 16 МБ данных
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp --buffer-type lockfree --producers 1 --consumers 1 --buffer-size_mb 4 --total-transfer_mb 16

# Пример: concurrent_queue, запуск без GUI
./build/DonutBufferApp.app/Contents/MacOS/DonutBufferApp --nogui --buffer-type concurrent_queue --producers 2 --consumers 2 --buffer-size_mb 2 --total-transfer_mb 8
```
## Опции командной строки

### С++ точка входа (`DonutBufferApp`)
- `--nogui` &mdash; запуск без графического интерфейса. По умолчанию значение `true`.
- `--mutex-vs-lockfree` &mdash; выполнить тест сравнения `MutexRingBuffer` и `LockFreeRingBuffer` и выйти.
- `--concurrent-vs-lockfree` &mdash; выполнить тест `ConcurrentQueue` против `LockFreeRingBuffer` и выйти.
- `--buffer-type {lockfree, mutex, concurrent_queue}` &mdash; тип используемого буфера.
- `--producers N` &mdash; количество потоков-производителей.
- `--consumers N` &mdash; количество потоков-потребителей.
- `--buffer-size_mb N` &mdash; размер буфера в мегабайтах.
- `--total-transfer_mb N` &mdash; общий объём передаваемых данных через ринг-буфер в мегабайтах.

### Python точка входа (`python -m mcp`)
- `text` &mdash; обязательный текст команды пользователя.
- `--full-response` &mdash; выводить полную информацию вместо только намерения.
- `--provider {ollama, openai}` &mdash; LLM-провайдер (по умолчанию переменная `LLM_PROVIDER` или `ollama`).
- `--openai-key KEY` &mdash; API-ключ OpenAI (по умолчанию переменная `OPENAI_API_KEY`).
- `--model MODEL` &mdash; модель для выбранного провайдера (по умолчанию из `OLLAMA_MODEL` или `OPENAI_MODEL`).

### Переменные окружения
- `LLM_PROVIDER` &mdash; провайдер LLM по умолчанию (`ollama` если не задано).
- `OPENAI_API_KEY` &mdash; ключ API для OpenAI.
- `OPENAI_MODEL` &mdash; модель для OpenAI (`gpt-3.5-turbo` по умолчанию).
- `OLLAMA_MODEL` &mdash; модель для Ollama (`llama3` по умолчанию).


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

