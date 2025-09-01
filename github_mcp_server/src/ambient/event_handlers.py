"""
🎯 Event Handlers - Обработчики событий для Ambient Agent

Вынесены из ambient_agent.py для лучшей организации кода.
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

# Импортируем из родительского пакета
sys.path.append(str(Path(__file__).parent.parent))
from ..core.base_wizard import BaseWizard
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
    
    def handle_workflow_event(self, event: Event) -> None:
        """Обрабатывает события workflow"""
        # no debug prints
        workflow_name = event.data.get('workflow_name', 'Unknown')
        run_number = event.data.get('run_number', '?')
        event_type = event.data.get('event_type', 'изменился')
        
        self.print_info(f"🚀 Workflow {workflow_name} (#{run_number}) {event_type}")
        
        # Генерируем промпт ТОЛЬКО для упавших workflow
        prompt = self.prompt_generator.generate_prompt(event)
        if not prompt:
            return
        # Отправляем промпт и публикуем ответ в UI (без печати здесь)
        answer = self.agent_injector.send_prompt(prompt)
        if answer:
            try:
                from ..core.message_bus import UIEventBus
                UIEventBus.instance().publish_assistant_message(answer)
            except Exception:
                pass
    def handle_pr_created(self, event: Event) -> None:
        """Обрабатывает создание новых PR"""
        pr_number = event.data.get('pr_number', '?')
        pr_title = event.data.get('pr_title', 'No title')
        author = event.data.get('author', 'Unknown')
        
        self.print_info(f"📋 Анализирую новый PR #{pr_number}: {pr_title[:50]}...")
        self.print_info(f"👤 Автор: {author}")
        
        prompt = self.prompt_generator.generate_prompt(event)
        if not prompt:
            return
        answer = self.agent_injector.send_prompt(prompt)
        if answer:
            self.print_success("✅ Анализ PR отправлен в cursor-agent и получен ответ")
    
    def handle_manual_trigger(self, event: Event) -> None:
        """Обрабатывает ручные триггеры"""
        analysis_type = event.data.get('type', 'manual')
        content = event.data.get('content', 'No content')
        
        self.print_info(f"🎯 Выполняю ручной анализ: {analysis_type}")
        self.print_info(f"📝 Контент: {content[:100]}...")
        
        prompt = self.prompt_generator.generate_prompt(event)
        answer = self.agent_injector.send_prompt(prompt)
        if answer:
            self.print_success("✅ Ручной анализ отправлен в cursor-agent и получен ответ")
    
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