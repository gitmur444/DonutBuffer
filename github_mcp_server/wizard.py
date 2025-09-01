"""
🧙‍♂️ DonutBuffer AI Wizard - Main Module

Главный модуль мастера настройки AI-анализа DonutBuffer проекта.
"""

from pathlib import Path
from src.core.base_wizard import BaseWizard, Colors
from src.core.env_manager import EnvManager
from src.setup.github_setup import GitHubSetup
from src.setup.mcp_setup import MCPSetup
# IntegrationTest перемещён в tests/preflight/test_integration.py и вызывается раннером
from rich.console import Console

# Импортируем Ambient Agent для тестирования
import sys
sys.path.append(str(Path(__file__).parent))
from src.ambient.ambient_agent import AmbientAgent
import threading

console = Console()

class DonutAIWizard(BaseWizard):
    """Главный мастер настройки DonutBuffer AI интеграции"""
    
    def __init__(self):
        # Определяем DonutBuffer directory правильно
        current_dir = Path.cwd()
        if current_dir.name == "github_mcp_server":
            self.donut_dir = current_dir.parent  # DonutBuffer
        else:
            self.donut_dir = current_dir  # Уже в DonutBuffer
        
        # Инициализируем компоненты
        self.env_manager = EnvManager(self.donut_dir)
        self.github_setup = GitHubSetup(self.env_manager)
        self.mcp_setup = MCPSetup(self.donut_dir)
        
        # Загружаем переменные из .env файла если он существует
        self.env_manager.load_env_file()

    def run(self) -> None:
        """Главный метод запуска мастера"""
        self.print_header()
        
        try:
            # Предзапусковые проверки (1–5) через preflight runner
            # Одновременно собираем полный текстовый лог для передачи в TUI как историю
            from tests.preflight.runner import run_preflight
            import re
            # накапливаем динамическую историю префлайта
            preflight_lines: list[str] = []
            def on_progress(msg: str) -> None:
                # очищаем ANSI и добавляем строку (кроме кратких статусов ok/fail)
                ansi_escape = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
                clean = ansi_escape.sub("", msg).strip()
                if re.fullmatch(r"(?i)(dependencies|github|mcp|integration|ambient)\s*:\s*(ok|fail)", clean):
                    return
                if clean:
                    preflight_lines.append(clean)
                # обновлять TUI будем при запуске, передаём текущий снимок истории
            ok, _ = run_preflight(self.donut_dir, on_progress=on_progress)
            preflight_text = "\n".join(preflight_lines)
            if not ok:
                self.print_error("Предзапусковые проверки провалены")
                self.print_info("💡 Исправьте замечания и запустите мастер снова")
                return
            
            # Запускаем Ambient Agent в фоне (тихо)
            import os
            # Не навязываем режимы вывода из мастера
            self.start_ambient_agent_background_no_sig()
            # Запуск простого интерактивного режима
            from src.ui import run_interactive
            run_interactive(preflight_text)
            
        except KeyboardInterrupt:
            console.print(f"\n[yellow]⚠️  Настройка прервана пользователем[/yellow]")
        except Exception as e:
            import traceback
            self.print_error("Неожиданная ошибка:")
            traceback.print_exc()

    def print_header(self) -> None:
        """Печать заголовка мастера (коротко, без рамки)."""
        console.print("[bold blue]DonutBuffer AI Wizard - Магический помощник разработчика[/bold blue]")

    def print_success_message(self) -> None:
        """Убрано по требованиям дизайна (без итогового сообщения)."""
        return

    def launch_cursor_agent(self) -> None:
        """Запуск cursor-agent без моста."""
        try:
            import subprocess
            subprocess.run(["cursor-agent"])  # обычный запуск
        except KeyboardInterrupt:
            console.print(f"\n[cyan]👋 До встречи! Используйте 'cursor-agent' для продолжения работы.[/cyan]")
        except Exception as e:
            self.print_error(f"Ошибка запуска cursor-agent: {e}")
            console.print(f"[cyan]💡 Запустите вручную: cursor-agent[/cyan]")

    def start_ambient_agent_background_no_sig(self) -> None:
        """Стартует AmbientAgent в фоновом потоке без перехвата Ctrl+C."""
        try:
            import os
            self._ambient = AmbientAgent(self.donut_dir, install_signal_handlers=False)

            def _runner():
                silent = os.environ.get("AMBIENT_SILENT", "").strip().lower() in ("1", "true", "yes")
                if silent:
                    # Полностью глушим любые принты фоновых компонентов
                    def _silence(x):
                        for name in ("print_info", "print_success", "print_warning", "print_error"):
                            if hasattr(x, name):
                                try:
                                    setattr(x, name, lambda *a, **k: None)
                                except Exception:
                                    pass
                    _silence(self._ambient)
                    # Также глушим дочерние компоненты, если уже созданы
                    for comp_name in ("github_monitor", "event_system", "prompt_generator", "agent_injector", "event_handlers"):
                        comp = getattr(self._ambient, comp_name, None)
                        if comp is not None:
                            _silence(comp)
                self._ambient.start()

            t = threading.Thread(target=_runner, daemon=True)
            t.start()
        except Exception as e:
            self.print_warning(f"Не удалось запустить Ambient Agent в фоне: {e}")
    
    def test_ambient_system(self) -> bool:
        """Шаг 5: Тестирование Ambient Agent системы событий"""
        self.print_step(5, "Тестирование Ambient Agent")
        
        try:
            # Создаем экземпляр Ambient Agent
            ambient_agent = AmbientAgent(self.donut_dir)
            
            # Запускаем тест системы событий
            success = ambient_agent.test_event_system()
            
            if success:
                self.print_success("Ambient Agent система событий работает корректно")
                return True
            else:
                self.print_warning("Ambient Agent система событий не прошла тест")
                return False
                
        except Exception as e:
            self.print_warning(f"Ошибка тестирования Ambient Agent: {e}")
            self.print_info("💡 Ambient Agent может не работать, но основная интеграция готова")
            return False

def main():
    """Точка входа для запуска мастера"""
    wizard = DonutAIWizard()
    wizard.run()

if __name__ == "__main__":
    main() 