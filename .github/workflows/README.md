# GitHub Actions для DonutBuffer

Этот проект использует несколько GitHub Actions workflows для автоматического тестирования:

## 🚀 CI.yml - Основной рабочий процесс

**Триггеры:** Push и Pull Request в ветки `master`, `main`, `develop`

### Включает 3 job'а:

1. **test** - Основные тесты на Linux (Ubuntu)
   - Тестирует на Ubuntu Latest и Ubuntu 20.04
   - Использует GCC и GCC-10
   - Запускает:
     - Unit тесты (`ringbuffer_tests`)
     - E2E тесты (`e2e_buffer_tests`)
     - Все тесты через CTest
     - Быстрая проверка производительности CLI

2. **test-macos** - Тесты на macOS
   - Аналогичные тесты на macOS для кроссплатформенности

3. **performance-tests** - Расширенные тесты производительности
   - Запускается только после успешного прохождения основных тестов
   - Тестирует различные конфигурации BufferRunner:
     - Mutex (1P+1C)
     - Lockfree (1P+1C)
     - Multi-threaded (4P+2C)
     - Stress test (8P+8C)

## ⚡ Quick-Test.yml - Быстрые проверки

**Триггеры:** Push во все ветки кроме `master`, `main`, `develop`

- Быстрая сборка и запуск только unit тестов
- Использует кеширование для ускорения
- Подходит для feature веток и экспериментов

## 🔧 Зависимости

Workflows автоматически устанавливают необходимые зависимости:
- **Linux:** build-essential, cmake, gcc-10, g++-10, libglfw3-dev и др.
- **macOS:** cmake, glfw через brew

## 📊 Результаты

- ✅ Зеленая галочка = все тесты прошли успешно
- ❌ Красный крестик = есть падающие тесты
- 🟡 Желтый кружок = workflow выполняется

## 🛠️ Локальная разработка

Для локального запуска тех же тестов:
```bash
# Полный набор тестов
./run-tests.sh

# Отдельные типы тестов
./run-tests.sh unit
./run-tests.sh e2e  
./run-tests.sh cli

# Через Makefile
make test
make test-unit
make test-e2e
```