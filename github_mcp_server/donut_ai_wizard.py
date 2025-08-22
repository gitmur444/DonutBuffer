#!/usr/bin/env python3
"""
🧙‍♂️ DonutBuffer AI Wizard

Магический помощник для настройки AI-анализа DonutBuffer проекта.
Выполняет настройку интеграции с GitHub.

Этот файл теперь использует модульную архитектуру для лучшей читаемости.
Основная логика разбита на следующие модули:

- core.py - базовые классы и утилиты
- env_manager.py - работа с .env файлами  
- dependencies.py - проверка зависимостей
- github_setup.py - настройка GitHub токена
- mcp_setup.py - настройка MCP сервера
- integration_test.py - тестирование интеграции
- wizard.py - главный класс мастера
"""

# Импортируем новый модульный мастер
from wizard import DonutAIWizard

def main():
    """Точка входа для запуска мастера"""
    wizard = DonutAIWizard()
    wizard.run()

if __name__ == "__main__":
    main() 