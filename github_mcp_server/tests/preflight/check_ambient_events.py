from pathlib import Path

from src.core.base_wizard import BaseWizard
from src.core.env_manager import EnvManager
from src.ambient.event_system import EventSystem, EventType
from src.ambient.github_monitor import GitHubMonitor
from src.ambient.prompt_generator import PromptGenerator
from src.ambient.agent_injector import AgentInjector
from src.ambient.event_handlers import EventHandlers


def run_ambient_events_check(donut_dir: Path) -> tuple[bool, str]:
    printer = BaseWizard()
    printer.print_step(6, "Тестирование Ambient событий (GITHUB_ISSUE_TEST)")

    try:
        env_manager = EnvManager(donut_dir)
        env_manager.load_env_file()

        event_system = EventSystem()
        github_monitor = GitHubMonitor(event_system, env_manager)
        prompt_generator = PromptGenerator()
        agent_injector = AgentInjector()
        event_handlers = EventHandlers(prompt_generator, agent_injector)

        # Регистрируем обработчик тестового события
        event_system.register_handler(EventType.GITHUB_ISSUE_TEST, event_handlers.handle_test_issue)

        # 1) Создаем тестовый issue
        issue = github_monitor.create_test_issue()
        issue_number = issue["number"]

        # 2) Запускаем систему и принудительно обрабатываем событие
        event_handlers.test_event_processed = False
        event_system.start_processing()
        github_monitor.force_check(issue_number)

        pending_count = event_system.get_pending_events_count()
        for _ in range(pending_count):
            if event_system.event_queue:
                event = event_system.event_queue.pop(0)
                event_system.process_event(event)

        ok = bool(event_handlers.test_event_processed)
        if not ok:
            printer.print_error("❌ E2E тест провален: событие не обработано")

        # Cleanup
        try:
            github_monitor.delete_test_issue(issue_number)
        finally:
            pass

        return ok, "ambient_events: ok" if ok else "ambient_events: fail"

    except Exception as e:
        printer.print_error(f"❌ Ambient Events тест провален: {e}")
        return False, "ambient_events: fail"


