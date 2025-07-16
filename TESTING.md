# 🎯 Тестирование DonutBuffer

## Быстрый старт

**Из корня проекта можно запускать тесты несколькими способами:**

### 1. 🚀 Через скрипты (рекомендуется)

```bash
# Все тесты
./run-tests.sh

# Короткий алиас
./test

# Только unit тесты
./test unit

# Только E2E тесты
./test e2e

# CLI производительность
./test cli

# Подробный вывод
./test all -v
```

### 2. 🔧 Через Makefile

```bash
# Все тесты
make test

# Отдельные виды тестов
make test-unit
make test-e2e
make test-cli
make test-verbose

# Быстрые команды (прямой CTest)
make test-quick
make test-quick-verbose

# Справка
make help
```

### 3. ⚡ Прямые команды (если уже собрано)

```bash
# Из папки build
cd build
ctest              # все тесты
ctest -V           # подробный вывод
./tests/ringbuffer_tests    # только unit
./tests/e2e_buffer_tests ./BufferRunner  # только e2e
```

## Сборка и тестирование

### Первый запуск:

```bash
# Сборка с тестами
make build-with-tests

# Запуск тестов
./test
```

### Последующие запуски:

```bash
# Просто запуск (автоматическая пересборка если нужно)
./test
```

## Что тестируется

### 📊 Unit тесты
- Базовая функциональность mutex/lockfree ring buffer
- Граничные случаи (переполнение, пустой буфер)
- Многопоточная производительность
- **Результат:** ~85K items/sec (mutex), ~2.6M items/sec (lockfree)

### 🌐 E2E тесты
- Параметры командной строки CLI
- Производительность в реальных условиях
- Стресс-тестирование
- **Результат:** Проверка всех CLI сценариев

### ⚡ CLI тесты
- Бенчмарки с разными конфигурациями
- Сравнение mutex vs lockfree
- **Результат:** Детальные метрики производительности

## Структура

```
DonutBuffer/
├── run-tests.sh         # Основной скрипт тестирования
├── test                 # Короткий алиас
├── Makefile            # Make команды
├── build/              # Директория сборки с тестами
│   ├── tests/
│   │   ├── ringbuffer_tests      # Unit тесты
│   │   └── e2e_buffer_tests      # E2E тесты
│   └── BufferRunner             # CLI версия
└── tests/              # Исходники тестов
    ├── ringbuffer_tests.cpp
    ├── e2e_buffer_tests.cpp
    └── README.md
```

## Результаты

Типичные результаты производительности:

| Тип теста | Mutex | Lockfree | Ускорение |
|-----------|-------|----------|-----------|
| Unit (2P+2C) | 85K items/sec | 2.6M items/sec | **30x** |
| E2E (2P+2C) | 376K items/sec | 2.5M items/sec | **6.6x** |
| CLI (8P+8C) | - | 2.4M items/sec | - |

**Вывод:** Lockfree реализация значительно превосходит mutex версию! 