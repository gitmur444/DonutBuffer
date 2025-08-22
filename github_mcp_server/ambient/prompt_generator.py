"""
💬 Prompt Generator - Генерация промптов для анализа

Создает структурированные промпты для различных типов анализа.
"""

import time
from typing import Dict, Any, List
import sys
from pathlib import Path

# Импортируем из родительского пакета
sys.path.append(str(Path(__file__).parent.parent))
from core import BaseWizard
from .event_system import Event, EventType

class PromptGenerator(BaseWizard):
    """Генератор промптов для анализа событий"""
    
    def __init__(self):
        self.prompt_templates = self.load_templates()
        
    def load_templates(self) -> Dict[str, str]:
        """Загружает шаблоны промптов"""
        return {
            "test_failure": """🔍 **АНАЛИЗ УПАВШИХ ТЕСТОВ DONUTBUFFER**

**Репозиторий:** {repo_name}
**Workflow:** {workflow_name} (Run #{run_number})
**Время:** {timestamp}
**URL:** {html_url}

**Упавшие задачи:**
```
{logs}
```

**Последний коммит:**
- **Автор:** {commit_author}
- **Сообщение:** {commit_message}
- **SHA:** {commit_sha}

**ЗАДАЧА:**
1. Проанализируй причины падения тестов
2. Определи связь с последними изменениями в C++ коде
3. Проверь влияние на производительность ring buffer
4. Предложи конкретные исправления
5. Оцени влияние на lockfree vs mutex реализации

**ФОКУС:** DonutBuffer C++ ring buffer, многопоточность, производительность""",

            "build_failure": """🛠️ **АНАЛИЗ ОШИБОК СБОРКИ DONUTBUFFER**

**Workflow:** {workflow_name} (Run #{run_number})
**Время:** {timestamp}

**Ошибки сборки:**
```
{logs}
```

**ЗАДАЧА:**
1. Определи причины ошибок компиляции
2. Проверь совместимость с C++20
3. Проанализируй проблемы с зависимостями
4. Предложи исправления для CMake конфигурации

**ФОКУС:** C++20, CMake, многопоточность, template метапрограммирование""",

            "pr_analysis": """📋 **АНАЛИЗ НОВОГО PULL REQUEST**

**PR #{pr_number}:** {pr_title}
**Автор:** {author}
**URL:** {pr_url}

**ЗАДАЧА:**
1. Проанализируй изменения в контексте DonutBuffer архитектуры
2. Оцени влияние на производительность ring buffer
3. Проверь соответствие паттернам lockfree программирования
4. Предложи улучшения для кода review

**ФОКУС:** Архитектура, производительность, best practices C++""",

            "manual_analysis": """🎯 **РУЧНОЙ АНАЛИЗ DONUTBUFFER**

**Запрошенный анализ:** {analysis_type}
**Данные:**
```
{data}
```

**ЗАДАЧА:** 
Проведи глубокий анализ с фокусом на:
- C++ ring buffer оптимизацию
- Многопоточное программирование  
- Lockfree vs mutex performance
- Memory ordering и cache efficiency

**КОНТЕКСТ:** DonutBuffer - высокопроизводительный ring buffer проект"""
        }
    
    def generate_prompt(self, event: Event) -> str:
        """
        Генерирует промпт на основе события
        
        Args:
            event: Событие для анализа
            
        Returns:
            str: Сгенерированный промпт
        """
        
        if event.type == EventType.GITHUB_TEST_FAILED:
            return self.generate_test_failure_prompt(event)
        elif event.type == EventType.GITHUB_BUILD_FAILED:
            return self.generate_build_failure_prompt(event)
        elif event.type == EventType.GITHUB_PR_CREATED:
            return self.generate_pr_analysis_prompt(event)
        elif event.type == EventType.MANUAL_TRIGGER:
            return self.generate_manual_analysis_prompt(event)
        elif event.type == EventType.GITHUB_ISSUE_TEST:
            return self.generate_test_issue_prompt(event)
        else:
            return self.generate_generic_prompt(event)
    
    def generate_test_failure_prompt(self, event: Event) -> str:
        """Генерирует промпт для анализа упавших тестов"""
        data = event.data
        
        # Извлекаем информацию о коммите
        head_commit = data.get("head_commit", {})
        commit_author = head_commit.get("author", {}).get("name", "Unknown")
        commit_message = head_commit.get("message", "No message")
        commit_sha = head_commit.get("id", "Unknown")[:8]
        
        return self.prompt_templates["test_failure"].format(
            repo_name=self.extract_repo_name(data),
            workflow_name=data.get("workflow_name", "Unknown"),
            run_number=data.get("run_number", "?"),
            timestamp=self.format_timestamp(event.timestamp),
            html_url=data.get("html_url", "N/A"),
            logs=data.get("logs", "Логи недоступны"),
            commit_author=commit_author,
            commit_message=commit_message,
            commit_sha=commit_sha
        )
    
    def generate_build_failure_prompt(self, event: Event) -> str:
        """Генерирует промпт для анализа ошибок сборки"""
        data = event.data
        
        return self.prompt_templates["build_failure"].format(
            workflow_name=data.get("workflow_name", "Unknown"),
            run_number=data.get("run_number", "?"),
            timestamp=self.format_timestamp(event.timestamp),
            logs=data.get("logs", "Логи недоступны")
        )
    
    def generate_pr_analysis_prompt(self, event: Event) -> str:
        """Генерирует промпт для анализа PR"""
        data = event.data
        
        return self.prompt_templates["pr_analysis"].format(
            pr_number=data.get("pr_number", "?"),
            pr_title=data.get("pr_title", "No title"),
            author=data.get("author", "Unknown"),
            pr_url=data.get("pr_url", "N/A")
        )
    
    def generate_manual_analysis_prompt(self, event: Event) -> str:
        """Генерирует промпт для ручного анализа"""
        data = event.data
        
        return self.prompt_templates["manual_analysis"].format(
            analysis_type=data.get("type", "General analysis"),
            data=data.get("content", "No additional data")
        )
    
    def generate_generic_prompt(self, event: Event) -> str:
        """Генерирует общий промпт для неизвестных типов событий"""
        return f"""🤖 **АНАЛИЗ СОБЫТИЯ DONUTBUFFER**

**Тип события:** {event.type.value}
**Источник:** {event.source}
**Время:** {self.format_timestamp(event.timestamp)}

**Данные:**
```
{self.format_event_data(event.data)}
```

**ЗАДАЧА:** 
Проанализируй это событие в контексте проекта DonutBuffer.
Фокус на C++ ring buffer, производительности и многопоточности.
"""
    
    def extract_repo_name(self, data: Dict) -> str:
        """Извлекает имя репозитория из данных"""
        # Попытаемся извлечь из URL
        html_url = data.get("html_url", "")
        if "github.com" in html_url:
            parts = html_url.split("/")
            if len(parts) >= 5:
                return f"{parts[-4]}/{parts[-3]}"
        
        return "DonutBuffer"
    
    def format_timestamp(self, timestamp: float) -> str:
        """Форматирует временную метку"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    
    def format_event_data(self, data: Dict[str, Any]) -> str:
        """Форматирует данные события для отображения"""
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for subkey, subvalue in value.items():
                    lines.append(f"  {subkey}: {subvalue}")
            elif isinstance(value, list):
                lines.append(f"{key}: {len(value)} items")
            else:
                # Ограничиваем длинные значения
                str_value = str(value)
                if len(str_value) > 200:
                    str_value = str_value[:200] + "..."
                lines.append(f"{key}: {str_value}")
        
        return "\n".join(lines)
    
    def create_custom_prompt(self, 
                           analysis_type: str, 
                           content: str, 
                           focus_areas: List[str] = None) -> str:
        """
        Создает кастомный промпт для ручного анализа
        
        Args:
            analysis_type: Тип анализа
            content: Контент для анализа
            focus_areas: Области фокуса
        """
        
        focus_text = ""
        if focus_areas:
            focus_text = f"\n**Области фокуса:** {', '.join(focus_areas)}"
        
        return f"""🎯 **КАСТОМНЫЙ АНАЛИЗ DONUTBUFFER**

**Тип анализа:** {analysis_type}
**Время:** {time.strftime("%Y-%m-%d %H:%M:%S")}

**Контент для анализа:**
```
{content}
```

**ЗАДАЧА:**
Проведи детальный анализ с учетом специфики DonutBuffer проекта.
Фокусируйся на C++ производительности, ring buffer архитектуре,
lockfree vs mutex реализациях.{focus_text}

**КОНТЕКСТ:** DonutBuffer - высокопроизводительный C++ ring buffer"""
        
        return template.format(**data)
    
    def generate_test_issue_prompt(self, event: Event) -> str:
        """Генерирует промпт для E2E тестового события"""
        issue_number = event.data.get('issue_number', '?')
        title = event.data.get('title', 'No title')
        
        return f"""🔬 **E2E ТЕСТ AMBIENT AGENT СИСТЕМЫ**

**GitHub Issue:** #{issue_number}
**Заголовок:** {title}
**Время:** {self.format_timestamp(event.timestamp)}

✅ **ТЕСТ УСПЕШЕН!**

Ambient Agent система событий работает корректно:
- GitHub API мониторинг ✅
- Система событий ✅  
- Обработчики событий ✅
- Генерация промптов ✅

DonutBuffer AI готов к работе! 🚀""" 