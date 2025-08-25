"""
📡 Event System - Система событий для Ambient Agent

Простая event-driven система для обработки триггеров.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
import threading
import sys
from pathlib import Path

# Импортируем из родительского пакета
sys.path.append(str(Path(__file__).parent.parent))
from ..core.base import BaseWizard

class EventType(Enum):
    """Типы событий в системе"""
    GITHUB_WORKFLOW_EVENT = "github_workflow_event"  # Любые события с workflows
    GITHUB_PR_CREATED = "github_pr_created"
    SYSTEM_ERROR = "system_error"
    MANUAL_TRIGGER = "manual_trigger"
    SYSTEM_TEST = "system_test"  # Для тестирования системы событий
    GITHUB_ISSUE_TEST = "github_issue_test"  # E2E тест через GitHub Issues

@dataclass
class Event:
    """Событие в системе"""
    type: EventType
    data: Dict[str, Any]
    timestamp: float
    source: str
    priority: int = 1  # 1=низкий, 5=критический
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

class EventSystem(BaseWizard):
    """Система событий для управления триггерами"""
    
    def __init__(self):
        self.handlers: Dict[EventType, List[Callable]] = {}
        self.event_queue: List[Event] = []
        self.running = False
        self.processing_thread: Optional[threading.Thread] = None
        
    def register_handler(self, event_type: EventType, handler: Callable) -> None:
        """
        Регистрирует обработчик для типа события
        
        Args:
            event_type: Тип события
            handler: Функция-обработчик
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        
        self.handlers[event_type].append(handler)
    
    def emit(self, event: Event) -> None:
        """
        Генерирует событие
        
        Args:
            event: Событие для обработки
        """
        self.event_queue.append(event)
        self.event_queue.sort(key=lambda e: (-e.priority, e.timestamp))
    
    def emit_simple(self, 
                   event_type: EventType, 
                   data: Dict[str, Any], 
                   source: str = "unknown",
                   priority: int = 1) -> None:
        """
        Упрощенная генерация события
        """
        event = Event(
            type=event_type,
            data=data,
            timestamp=time.time(),
            source=source,
            priority=priority
        )
        self.emit(event)
    
    def start_processing(self) -> None:
        """Запускает обработку событий в фоновом потоке"""
        if self.running:
            return
            
        self.running = True
        self.processing_thread = threading.Thread(
            target=self.process_events_loop, 
            daemon=True
        )
        self.processing_thread.start()
    
    def stop_processing(self) -> None:
        """Останавливает обработку событий"""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        self.print_info("📡 Система событий остановлена")
    
    def process_events_loop(self) -> None:
        """Основной цикл обработки событий"""
        while self.running:
            try:
                if self.event_queue:
                    event = self.event_queue.pop(0)
                    self.process_event(event)
                else:
                    time.sleep(1)  # Небольшая пауза если нет событий
            except Exception as e:
                self.print_error(f"Ошибка в цикле событий: {e}")
                time.sleep(5)  # Пауза при ошибке
    
    def process_event(self, event: Event) -> None:
        """
        Обрабатывает одно событие
        
        Args:
            event: Событие для обработки
        """
        if event.type in self.handlers:
            for handler in self.handlers[event.type]:
                try:
                    handler(event)
                except Exception as e:
                    self.print_error(f"Ошибка в обработчике {handler.__name__}: {e}")
        else:
            # Показываем только для неизвестных событий
            event_descriptions = {
                EventType.GITHUB_WORKFLOW_EVENT: "🚀 событие workflow",
                EventType.GITHUB_PR_CREATED: "📋 новый Pull Request",
                EventType.MANUAL_TRIGGER: "🎯 ручной запрос анализа",
                EventType.SYSTEM_TEST: "🧪 системный тест",
                EventType.GITHUB_ISSUE_TEST: "🔬 E2E тест через GitHub Issue"
            }
            description = event_descriptions.get(event.type, event.type.value)
            self.print_warning(f"Нет обработчиков для {description}")
    
    def get_pending_events_count(self) -> int:
        """Возвращает количество событий в очереди"""
        return len(self.event_queue)
    
    def clear_queue(self) -> None:
        """Очищает очередь событий"""
        cleared = len(self.event_queue)
        self.event_queue.clear()
        self.print_info(f"🧹 Очищено {cleared} событий из очереди") 