# 🚀 DonutBuffer GitHub MCP Integration

Интеграция Cursor Agent с GitHub CI/CD для проекта DonutBuffer.

## 📋 Быстрый старт

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка
```bash
# Установите GitHub токен
export GITHUB_TOKEN="your_token_here"

# Запустите автоматическую настройку
python setup_github_integration.py
```

### 3. Тестирование
```bash
# Проверка интеграции
python test_mcp_connection.py

# Запуск MCP сервера
python start_mcp_server.py

# Мониторинг CI/CD
python check_cicd.py
```

## 🎯 Примеры использования

### Анализ упавших тестов
```bash
cursor-agent "Какие тесты упали в DonutBuffer ночью?"
cursor-agent "Покажи логи последнего failed workflow"
```

### Мониторинг производительности
```bash
cursor-agent "Анализ производительности C++ тестов DonutBuffer"
cursor-agent "Предложи оптимизации для ring buffer тестов"
```

### Работа с Pull Requests
```bash
cursor-agent "Статус PR с изменениями в lockfree ring buffer"
cursor-agent "Анализ code review для последнего PR"
```

## 📁 Структура файлов

- `setup_github_integration.py` - Автоматическая настройка
- `test_mcp_connection.py` - Тестирование интеграции
- `start_mcp_server.py` - Запуск MCP сервера
- `check_cicd.py` - Мониторинг CI/CD
- `mcp_config.json` - Конфигурация MCP
- `requirements.txt` - Python зависимости

## 🔧 Настройка GitHub Token

1. Перейдите: https://github.com/settings/tokens?type=beta
2. Создайте Fine-grained personal access token
3. Выберите репозитории (DonutBuffer)
4. Добавьте права:
   - Actions: Read & Write
   - Contents: Read
   - Pull requests: Read & Write
   - Metadata: Read

## 🚀 Интеграция в DonutBuffer workflow

Добавьте в ваш GitHub Actions:

```yaml
- name: AI Analysis
  run: |
    export GITHUB_TOKEN="${{ secrets.GITHUB_TOKEN }}"
    python DonutBuffer/github_mcp_server/check_cicd.py
```

---

Интеграция специально оптимизирована для C++ проекта DonutBuffer с фокусом на:
- 🧪 Анализ производительности ring buffer тестов
- 🔄 Мониторинг lockfree vs mutex реализаций
- 📊 Отчеты о качестве кода и тестов
- 🛠️ Автоматические рекомендации по оптимизации
