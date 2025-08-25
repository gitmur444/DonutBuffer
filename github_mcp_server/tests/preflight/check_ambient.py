from pathlib import Path

from src.ambient.ambient_agent import AmbientAgent


def run_ambient_e2e_check(donut_dir: Path) -> tuple[bool, str]:
    agent = AmbientAgent(donut_dir, install_signal_handlers=False)
    # Явно печатаем шаг 5 в контексте агента
    agent.print_step(5, "Тестирование Ambient Agent")
    ok = agent.test_event_system()
    return ok, "ambient: ok" if ok else "ambient: fail"


