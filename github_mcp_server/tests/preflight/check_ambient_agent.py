from pathlib import Path
import threading
import time

from src.core.base_wizard import BaseWizard
from src.ambient.ambient_agent import AmbientAgent
from src.ambient.agent_injector import AgentInjector


def run_ambient_agent_check(donut_dir: Path) -> tuple[bool, str]:
    printer = BaseWizard()
    printer.print_step(5, "Тестирование Ambient Agent (session + ping)")

    try:
        # 1) Запускаем AmbientAgent в фоне
        agent = AmbientAgent(donut_dir, install_signal_handlers=False)
        th = threading.Thread(target=agent.start, daemon=True)
        th.start()
        time.sleep(2)

        # 2) Убеждаемся, что есть session_id и агент отвечает на ping
        injector = AgentInjector()
        from src.core.cursor_client import get_global_cursor_client
        client = get_global_cursor_client()
        session_id = client.ensure_session()
        if not session_id:
            printer.print_error("❌ Ambient: не удалось инициализировать session_id")
            return False, "ambient_agent: fail"

        resp = injector.send_prompt("Ambient preflight ping")
        if not (resp or "").strip():
            printer.print_error("❌ Ambient: cursor-agent не ответил на ping")
            return False, "ambient_agent: fail"

        return True, "ambient_agent: ok"

    except Exception as e:
        printer.print_error(f"❌ Ambient Agent старт/проверка провалены: {e}")
        return False, "ambient_agent: fail"


