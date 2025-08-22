"""
🎯 Event Handlers - Обработчики событий для Ambient Agent

Вынесены из ambient_agent.py для лучшей организации кода.
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Импортируем из родительского пакета
sys.path.append(str(Path(__file__).parent.parent))
from core import BaseWizard
from .event_system import Event, EventType

# Избегаем циклических импортов
if TYPE_CHECKING:
    from .prompt_generator import PromptGenerator
    from .agent_injector import AgentInjector

class EventHandlers(BaseWizard):
    """Класс для обработки различных типов событий"""
    
    def __init__(self, prompt_generator: "PromptGenerator", agent_injector: "AgentInjector"):
        """
        Инициализация обработчиков
        
        Args:
            prompt_generator: Генератор промптов
            agent_injector: Инжектор промптов в cursor-agent
        """
        super().__init__()
        self.prompt_generator = prompt_generator
        self.agent_injector = agent_injector
        self.test_event_processed = False  # Флаг для E2E теста
    
    def handle_test_failure(self, event: Event) -> None:
        """Обрабатывает падения тестов"""
        workflow_name = event.data.get('workflow_name', 'Unknown')
        run_number = event.data.get('run_number', '?')
        
        self.print_warning(f"🚨 Анализирую падение тестов: {workflow_name} (#{run_number})")
        
        # Генерируем промпт
        prompt = self.prompt_generator.generate_prompt(event)
        
        # Отправляем в cursor-agent
        success = self.agent_injector.inject_prompt(prompt, "test_failure")
        
        if success:
            self.print_success("✅ Анализ упавших тестов отправлен в cursor-agent")
            self.print_info("💡 Проверьте cursor-agent для диагностики проблем")
        else:
            self.print_error("❌ Не удалось отправить анализ в cursor-agent")
    
    def handle_build_failure(self, event: Event) -> None:
        """Обрабатывает ошибки сборки"""
        workflow_name = event.data.get('workflow_name', 'Unknown')
        
        self.print_warning(f"🛠️ Анализирую ошибку сборки: {workflow_name}")
        
        prompt = self.prompt_generator.generate_prompt(event)
        success = self.agent_injector.inject_prompt(prompt, "build_failure")
        
        if success:
            self.print_success("✅ Анализ ошибок сборки отправлен в cursor-agent")
            self.print_info("💡 Проверьте cursor-agent для исправления компиляции")
    
    def handle_pr_created(self, event: Event) -> None:
        """Обрабатывает создание новых PR"""
        pr_number = event.data.get('pr_number', '?')
        pr_title = event.data.get('pr_title', 'No title')
        author = event.data.get('author', 'Unknown')
        
        self.print_info(f"📋 Анализирую новый PR #{pr_number}: {pr_title[:50]}...")
        self.print_info(f"👤 Автор: {author}")
        
        prompt = self.prompt_generator.generate_prompt(event)
        success = self.agent_injector.inject_prompt(prompt, "pr_analysis")
        
        if success:
            self.print_success("✅ Анализ PR отправлен в cursor-agent")
            self.print_info("💡 Проверьте cursor-agent для code review рекомендаций")
    
    def handle_manual_trigger(self, event: Event) -> None:
        """Обрабатывает ручные триггеры"""
        analysis_type = event.data.get('type', 'manual')
        content = event.data.get('content', 'No content')
        
        self.print_info(f"🎯 Выполняю ручной анализ: {analysis_type}")
        self.print_info(f"📝 Контент: {content[:100]}...")
        
        prompt = self.prompt_generator.generate_prompt(event)
        success = self.agent_injector.inject_prompt(prompt, "manual_analysis")
        
        if success:
            self.print_success("✅ Ручной анализ отправлен в cursor-agent")
            self.print_info("💡 Проверьте cursor-agent для результатов анализа")
    
    def handle_system_test(self, event: Event) -> None:
        """Обрабатывает системный тест"""
        test_id = event.data.get('test_id', 'unknown')
        description = event.data.get('description', 'No description')
        
        self.print_success(f"🧪 Системный тест успешно обработан: {test_id}")
        self.print_info(f"📋 Описание: {description}")
        
        # Помечаем что тест обработан
        if hasattr(self, 'test_results'):
            self.test_results[test_id] = True
    
    def handle_test_issue(self, event: Event) -> None:
        """Обрабатывает E2E тест через GitHub Issues"""
        # Устанавливаем флаг что событие обработано
        self.test_event_processed = True 