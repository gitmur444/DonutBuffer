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
        agent.start_background()
        # Небольшая задержка, чтобы монитор начал опросы
        time.sleep(1.0)

        # 2) Убеждаемся, что есть session_id и агент отвечает на ping
        injector = AgentInjector()
        from src.core.cursor_client import get_global_cursor_client
        client = get_global_cursor_client()

        # ensure_session with timeout + progress logs
        session_box = {"sid": None}
        def _ensure():
            try:
                # Force creation of a fresh session and stop immediately once id is captured
                client._session_id = None  # reset
                client.send_stream("DonutBuffer ambient init", on_user=None, on_chunk=None, on_result=None, stop_on_session=True)
                session_box["sid"] = client.get_session_id()
            except Exception:
                session_box["sid"] = None
        th_ensure = threading.Thread(target=_ensure, daemon=True)
        th_ensure.start()
        start_ensure = time.time()
        waited = 0
        while th_ensure.is_alive() and waited < 30:
            time.sleep(1)
            waited = int(time.time() - start_ensure)
            # убираем периодические прогресс-логи
        th_ensure.join(timeout=0)
        if th_ensure.is_alive() or not session_box["sid"]:
            printer.print_error("❌ Ambient: не удалось инициализировать session_id (timeout)")
            return False, "ambient_agent: fail"
        else:
            pass

        # ping with timeout + progress logs
        resp_box = {"resp": None}
        def _ping():
            try:
                # For speed, request only the first chunk then stop
                from src.core.cursor_client import get_global_cursor_client
                client2 = get_global_cursor_client()
                acc = []
                def _on_chunk(t: str):
                    acc.append(t)
                client2.send_stream("Ambient preflight ping", on_chunk=_on_chunk, on_result=None, stop_on_first_chunk=True)
                resp_box["resp"] = "".join(acc)
            except Exception:
                resp_box["resp"] = ""
        th_ping = threading.Thread(target=_ping, daemon=True)
        th_ping.start()
        start_ping = time.time()
        waited = 0
        while th_ping.is_alive() and waited < 30:
            time.sleep(1)
            waited = int(time.time() - start_ping)
            # убираем периодические прогресс-логи пинга
        th_ping.join(timeout=0)
        if th_ping.is_alive() or not (resp_box["resp"] or "").strip():
            printer.print_error("❌ Ambient: cursor-agent не ответил на ping (timeout)")
            return False, "ambient_agent: fail"
        else:
            pass

        # Агент остаётся запущенным для последующих шагов префлайта
        printer.print_success("Ambient Agent работает: session_id получен, ping ок")

        return True, "ambient_agent: ok"

    except Exception as e:
        printer.print_error(f"❌ Ambient Agent старт/проверка провалены: {e}")
        return False, "ambient_agent: fail"


