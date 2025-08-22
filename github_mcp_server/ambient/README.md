# 🤖 DonutBuffer Ambient Agent

**Автоматический мониторинг и анализ проекта через cursor-agent**

Система фонового мониторинга GitHub, которая автоматически обнаруживает падения тестов, ошибки сборки и другие события, генерирует анализ и отправляет его в cursor-agent для работы пользователя.

## 🏗️ Архитектура

```
Ambient Agent System
├── 🤖 AmbientAgent        - главный orchestrator  
├── 📡 EventSystem         - система событий/триггеров
├── 🔍 GitHubMonitor       - мониторинг GitHub API
├── 💬 PromptGenerator     - генерация промптов для анализа
└── 🚀 AgentInjector      - инжекция в cursor-agent
```

## ⚡ Быстрый старт

### 1. Базовая настройка
```bash
# Из корня DonutBuffer проекта
./wizard                    # Настройка GitHub интеграции
```

### 2. Запуск Ambient Agent
```bash
./ambient-agent start       # Запуск фонового мониторинга
./ambient-agent test        # Тест системы
./ambient-agent status      # Проверка статуса  
./ambient-agent stop        # Остановка
```

## 🎯 Возможности

### 🔍 **Автоматический мониторинг:**
- **Падения тестов** в GitHub Actions
- **Ошибки сборки** C++ проекта
- **Новые Pull Requests** для code review
- **Изменения в репозитории**

### 💬 **Умная генерация промптов:**
- **Контекстные анализы** с фокусом на DonutBuffer
- **Структурированные запросы** для C++ ring buffer
- **Специфичные для lockfree vs mutex** рекомендации
- **Автоматическое извлечение логов** и коммитов

### 🚀 **Интеграция с cursor-agent:**
- **Автоматическая отправка** анализа в cursor-agent
- **Fallback в файлы** если cursor-agent недоступен
- **Prioritized events** - критические события первыми

## 📋 Workflow

1. **🔍 Мониторинг** - система опрашивает GitHub API каждые 60 секунд
2. **📡 События** - при падении тестов генерируется событие  
3. **💬 Промпт** - система создает структурированный анализ
4. **🚀 Инжекция** - анализ отправляется в cursor-agent автоматически
5. **👤 Работа** - пользователь видит готовый анализ и может продолжить

## 🧪 Примеры событий

### Падение тестов:
```
🔍 АНАЛИЗ УПАВШИХ ТЕСТОВ DONUTBUFFER

Репозиторий: user/DonutBuffer  
Workflow: CI Tests (Run #123)
Время: 2024-08-22 15:30:00

Упавшие задачи:
❌ Job: build-and-test
  ❌ Step: Run tests

Последний коммит:
- Автор: developer
- Сообщение: Optimize ring buffer performance  
- SHA: abc12345

ЗАДАЧА:
1. Проанализируй причины падения тестов
2. Определи связь с последними изменениями в C++ коде
3. Проверь влияние на производительность ring buffer
4. Предложи конкретные исправления
5. Оцени влияние на lockfree vs mutex реализации
```

### Новый PR:
```
📋 АНАЛИЗ НОВОГО PULL REQUEST

PR #45: Add memory ordering optimizations
Автор: contributor

ЗАДАЧА:
1. Проанализируй изменения в контексте DonutBuffer архитектуры
2. Оцени влияние на производительность ring buffer
3. Проверь соответствие паттернам lockfree программирования
4. Предложи улучшения для кода review
```

## ⚙️ Конфигурация

### Настройки мониторинга:
- **Интервал проверки:** 60 секунд
- **Поддерживаемые события:** падения тестов, ошибки сборки, новые PR
- **Приоритизация:** критические события обрабатываются первыми

### Системные требования:
- ✅ **Python 3.7+** 
- ✅ **requests** модуль
- ✅ **cursor-agent** CLI
- ✅ **GitHub токен** (настраивается через ./wizard)

## 🔧 API для ручных триггеров

```python
from ambient import AmbientAgent
from pathlib import Path

# Инициализация
agent = AmbientAgent(Path.cwd())

# Ручной анализ
agent.trigger_manual_analysis(
    analysis_type="performance_review",
    content="Benchmark results showing regression in lockfree implementation..."
)
```

## 📊 Мониторинг

### Логи и статус:
```bash
./ambient-agent status      # Проверка процессов
tail -f ~/.cursor/ambient/  # Логи ambient системы
```

### Сохраненные промпты:
```bash
ls ~/.cursor/ambient/       # Список сохраненных анализов
cat ~/.cursor/ambient/test_failure_*.md  # Просмотр анализа
```

## 🚀 Расширения

Система легко расширяется новыми типами событий:

1. **Добавить EventType** в `event_system.py`
2. **Создать шаблон промпта** в `prompt_generator.py`  
3. **Добавить обработчик** в `ambient_agent.py`
4. **Зарегистрировать источник** в `github_monitor.py`

## 🔒 Безопасность

- ✅ **GitHub токен** хранится в `.env` (не в git)
- ✅ **Логи ограничены** по размеру (защита от спама)
- ✅ **Graceful shutdown** (Ctrl+C)
- ✅ **Error handling** во всех компонентах

---

*Создано специально для высокопроизводительного C++ ring buffer проекта* 🍩 