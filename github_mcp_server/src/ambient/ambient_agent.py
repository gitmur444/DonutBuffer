"""
🤖 Ambient Agent - Главный orchestrator

Связывает все компоненты системы: мониторинг, события, генерацию промптов и инжекцию.
"""

import time
import signal
import sys
from pathlib import Path
from typing import Optional

# Импортируем из родительского пакета
sys.path.append(str(Path(__file__).parent.parent))
from ..core.base_wizard import BaseWizard
from ..core.env_manager import EnvManager

# Импортируем ambient компоненты
from .event_system import EventSystem, Event, EventType
from .github_monitor import GitHubMonitor
from .prompt_generator import PromptGenerator
from .agent_injector import AgentInjector
from .event_handlers import EventHandlers

class AmbientAgent(BaseWizard):
    """Главный ambient agent для автоматического мониторинга и анализа"""
    
    def __init__(self, donut_dir: Path, install_signal_handlers: bool = True):
        self.donut_dir = donut_dir
        self.running = False
        
        # Инициализируем компоненты
        self.env_manager = EnvManager(donut_dir)
        self.env_manager.load_env_file()
        
        self.event_system = EventSystem()
        self.github_monitor = GitHubMonitor(self.event_system, self.env_manager)
        self.prompt_generator = PromptGenerator()
        self.agent_injector = AgentInjector()
        
        # Создаем обработчики событий
        self.event_handlers = EventHandlers(self.prompt_generator, self.agent_injector)
        
        # Регистрируем обработчики событий
        self.setup_event_handlers()
        
        # Настраиваем обработку сигналов для graceful shutdown (опционально)
        if install_signal_handlers:
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_event_handlers(self) -> None:
        """Настраивает обработчики событий"""
        
        # Регистрируем обработчики событий
        self.event_system.register_handler(EventType.GITHUB_WORKFLOW_EVENT, self.event_handlers.handle_workflow_event)
        self.event_system.register_handler(EventType.GITHUB_PR_CREATED, self.event_handlers.handle_pr_created)
        self.event_system.register_handler(EventType.MANUAL_TRIGGER, self.event_handlers.handle_manual_trigger)
        self.event_system.register_handler(EventType.SYSTEM_TEST, self.event_handlers.handle_system_test)
        self.event_system.register_handler(EventType.GITHUB_ISSUE_TEST, self.event_handlers.handle_test_issue)

    
    def start(self) -> None:
        """Запускает ambient agent"""
        self.print_info("🤖 Запускаю DonutBuffer Ambient Agent...")
        
        # Префлайт-проверки выполняются в ./wizard через tests/preflight/runner
        
        self.running = True
        
        # Запускаем систему событий
        self.print_info("[ambient] starting event system")
        self.event_system.start_processing()
        
        # Запускаем мониторинг GitHub
        self.print_info("[ambient] starting GitHub monitor")
        if self.github_monitor.start_monitoring():
            self.print_success("🔍 GitHub мониторинг активен")
        else:
            self.print_warning("⚠️ GitHub мониторинг не запущен (проверьте токен)")
        
        self.print_success("🤖 Ambient Agent запущен и работает в фоне")
        self.print_info("💡 Нажмите Ctrl+C для остановки")
        
        # Основной цикл
        try:
            self.main_loop()
        except KeyboardInterrupt:
            self.print_info("\n⚠️ Получен сигнал остановки...")
        finally:
            self.stop()
    
    # Префлайт-проверка перенесена в tests/preflight/runner.py
    
    def main_loop(self) -> None:
        """Основной цикл ambient agent"""
        while self.running:
            try:                
                # Ожидаем
                time.sleep(300)  # 5 минут
                
            except Exception as e:
                self.print_error(f"Ошибка в main loop: {e}")
                time.sleep(60)
    
    def get_uptime(self) -> str:
        """Возвращает время работы"""
        if hasattr(self, 'start_time'):
            uptime_seconds = time.time() - self.start_time
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return f"{hours}ч {minutes}м"
        return "0м"
    
    def stop(self) -> None:
        """Останавливает ambient agent"""
        self.print_info("🛑 Останавливаю Ambient Agent...")
        
        self.running = False
        
        # Останавливаем компоненты
        self.github_monitor.stop_monitoring()
        self.event_system.stop_processing()
        
        self.print_success("🤖 Ambient Agent остановлен")
    
    def signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        self.print_info(f"\n📡 Получен сигнал {signum}")
        self.running = False
    
    def trigger_manual_analysis(self, analysis_type: str, content: str) -> None:
        """Запускает ручной анализ"""
        
        self.event_system.emit_simple(
            event_type=EventType.MANUAL_TRIGGER,
            data={
                "type": analysis_type,
                "content": content
            },
            source="manual",
            priority=3
        )
        
        self.print_success(f"🎯 Запущен ручной анализ: {analysis_type}")
    
    # E2E проверка вынесена в tests/preflight/check_ambient.py

if __name__ == "__main__":
    # Простой способ запуска для тестирования
    donut_dir = Path.cwd()
    if donut_dir.name == "ambient":
        donut_dir = donut_dir.parent.parent
    
    agent = AmbientAgent(donut_dir)
    agent.start() 