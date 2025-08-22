# 🍩 DonutBuffer GitHub Integration - Wrapper Commands

## ⚡ Супер-удобные команды одной строкой!

Теперь все команды автоматически **активируют Python venv** и **запускают нужные скрипты**:

```bash
# Настройка (создает venv, устанавливает зависимости, настраивает GitHub интеграцию)
github_mcp_server/setup-github

# Тестирование интеграции
github_mcp_server/test-github

# Демонстрация возможностей
github_mcp_server/demo-github

# Запуск MCP сервера
./start-mcp

# Мониторинг CI/CD
./check-cicd
```

## 🎯 Быстрый старт

```bash
# 1. Одна команда для полной настройки
github_mcp_server/setup-github

# 2. Тестирование
github_mcp_server/test-github

# 3. Запуск (в отдельном терминале)
./start-mcp

# 4. Использование Cursor Agent
cursor-agent "Анализ DonutBuffer CI/CD"
```

## 📂 Что создается

| Файл/Папка | Назначение |
|------------|------------|
| `venv/` | Виртуальная среда Python (создается автоматически) |
| `github_mcp_server/` | Python скрипты интеграции |
| `github_mcp_server/start_mcp_server.py` | Запуск MCP сервера (создается setup-github) |
| `github_mcp_server/check_cicd.py` | Мониторинг CI/CD (создается setup-github) |
| `github_mcp_server/mcp_config.json` | Конфигурация MCP (создается setup-github) |

## 🔧 Wrapper скрипты

### 📁 В папке github_mcp_server/

- `setup-github` - Автоматическая настройка с созданием venv в корне DonutBuffer
- `test-github` - Тестирование интеграции
- `demo-github` - Демонстрация команд

### 📁 В корне DonutBuffer/

- `start-mcp` - Запуск GitHub MCP Server
- `check-cicd` - Анализ CI/CD статуса

**Каждая команда автоматически:**
- ✅ Проверяет наличие venv (в правильном месте)
- ✅ Активирует виртуальную среду
- ✅ Запускает соответствующий Python скрипт
- ✅ Выводит полезные подсказки

## 📖 Полная документация

Детальная документация находится в:
- `github_mcp_server/README.md` - Полное руководство
- `github_mcp_server/QUICK_START.md` - Быстрый старт
- `github_mcp_server/DONUTBUFFER_GITHUB_INTEGRATION.md` - Специфичные возможности

## 🚀 Результат

После `./setup-github` ваш DonutBuffer проект получает:

✅ **AI-powered CI/CD анализ** через Cursor Agent  
✅ **Автоматический мониторинг** ring buffer тестов  
✅ **Performance regression detection** для C++ кода  
✅ **Memory leak analysis** и optimization suggestions  
✅ **Predictive analysis** потенциальных проблем  

**Команды для Cursor Agent:**
```bash
cursor-agent "Какие C++ тесты упали в DonutBuffer ночью?"
cursor-agent "Сравни производительность mutex vs lockfree реализаций"
cursor-agent "Анализ memory usage в ring buffer за последнюю неделю"
cursor-agent "Предложи оптимизации для CMake сборки"
```

---

**🎉 Готово! Одна команда `./setup-github` и у вас есть AI-powered анализ CI/CD для DonutBuffer!** 