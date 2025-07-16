# DonutBuffer - Тесты

Этот проект содержит комплексную систему тестирования для ring buffer реализаций.

## Структура тестов

### 1. Unit-тесты (`ringbuffer_tests.cpp`)

**Базовые тесты:**
- `test_mutex_basic()` - основная функциональность MutexRingBuffer
- `test_lockfree_basic()` - основная функциональность LockFreeRingBuffer

**Тесты граничных случаев:**
- `test_mutex_buffer_full()` - поведение при переполнении буфера
- `test_lockfree_buffer_full()` - поведение при переполнении буфера
- `test_mutex_empty_buffer()` - поведение при пустом буфере
- `test_lockfree_empty_buffer()` - поведение при пустом буфере

**Многопоточные тесты:**
- `test_mutex_multithreaded()` - тест производительности с несколькими потоками
- `test_lockfree_multithreaded()` - тест производительности с несколькими потоками

### 2. E2E тесты (`e2e_buffer_tests.cpp`)

**Тесты параметров командной строки:**
- `test_default_parameters()` - проверка работы с параметрами по умолчанию
- `test_lockfree_type()` - проверка --type=lockfree
- `test_multiple_producers_consumers()` - проверка --producers=N --consumers=M
- `test_invalid_type()` - обработка некорректных типов буфера

**Тесты производительности:**
- `test_performance_reasonable()` - проверка разумной производительности (>10K items/sec)
- `test_stress_high_concurrency()` - стресс-тест с высокой нагрузкой
- `test_mutex_vs_lockfree_performance()` - сравнение производительности mutex vs lockfree

## Сборка и запуск

### Сборка проекта

```bash
mkdir build && cd build
cmake ..
make -j4
```

### Запуск тестов

**Все тесты через CTest:**
```bash
ctest --verbose
```

**Unit-тесты отдельно:**
```bash
./tests/ringbuffer_tests
```

**E2E тесты отдельно:**
```bash
./tests/e2e_buffer_tests ./BufferRunner
```

## Результаты тестов

### Типичная производительность

**Unit-тесты (многопоточные):**
- Mutex: ~80-100K items/sec
- Lockfree: ~2-3M items/sec

**CLI тесты:**
- Lockfree performance: ~3-4M items/sec
- Mutex performance: ~300-400K items/sec

### Интерпретация результатов

1. **Lockfree значительно быстрее** - в 6-10 раз по сравнению с mutex
2. **Высокая производительность** - lockfree обрабатывает миллионы элементов в секунду
3. **Стабильность** - все тесты проходят стабильно
4. **Масштабируемость** - производительность растет с количеством потоков

## Добавление новых тестов

### Для unit-тестов:

1. Добавьте функцию в `ringbuffer_tests.cpp`
2. Вызовите её в `main()`
3. Пересоберите проект

### Для e2e тестов:

1. Добавьте метод в класс `BufferRunnerE2ETests`
2. Вызовите его в `run_all_tests()`
3. Пересоберите проект

## Параметры для тестирования

CLI BufferRunner поддерживает следующие параметры:

- `--type=mutex|lockfree` - тип ring buffer
- `--producers=N` - количество производителей
- `--consumers=N` - количество потребителей

**Примеры:**

```bash
# Базовый тест
./BufferRunner

# Lockfree с 4 производителями и 2 потребителями
./BufferRunner --type=lockfree --producers=4 --consumers=2

# Стресс-тест
./BufferRunner --type=lockfree --producers=8 --consumers=8
```

## CI/CD интеграция

Тесты интегрированы в CMake и могут быть запущены через:

```bash
ctest
```

Это делает их пригодными для интеграции в системы непрерывной интеграции. 