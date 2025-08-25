"""
🧙‍♂️ DonutBuffer AI Wizard - Main Module

Главный модуль мастера настройки AI-анализа DonutBuffer проекта.
"""

from pathlib import Path
from src.core.base_wizard import BaseWizard, Colors
from src.core.env_manager import EnvManager
from src.core.dependency_checker import DependencyChecker
from src.setup.github_setup import GitHubSetup
from src.setup.mcp_setup import MCPSetup
from tests.integration.test_integration import IntegrationTest
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
        self.dependency_checker = DependencyChecker()
        self.github_setup = GitHubSetup(self.env_manager)
        self.mcp_setup = MCPSetup(self.donut_dir)
        self.integration_test = IntegrationTest(self.env_manager)
        
        # Загружаем переменные из .env файла если он существует
        self.env_manager.load_env_file()

    def run(self) -> None:
        """Главный метод запуска мастера"""
        self.print_header()
        
        try:
            # Предзапусковые проверки (1–5) через preflight runner
            from tests.preflight.runner import run_preflight
            ok, _ = run_preflight(self.donut_dir)
            if not ok:
                self.print_error("Предзапусковые проверки провалены")
                self.print_info("💡 Исправьте замечания и запустите мастер снова")
                return
            
            # Настройка завершена успешно
            self.print_success_message()
            
            # Запускаем Ambient Agent в фоне (тихо)
            import os
            os.environ["AMBIENT_SILENT"] = "1"
            self.start_ambient_agent_background_no_sig()
            # Запуск простого интерактивного режима
            from src.ui.interactive_simple import run_interactive
            run_interactive()
            
        except KeyboardInterrupt:
            console.print(f"\n[yellow]⚠️  Настройка прервана пользователем[/yellow]")
        except Exception as e:
            self.print_error(f"Неожиданная ошибка: {e}")

    def print_header(self) -> None:
        """Печать заголовка мастера"""
        console.print("[bold blue]🧙‍♂️ ════════════════════════════════════════════════════════════[/bold blue]")
        console.print("[bold blue]   DonutBuffer AI Wizard - Магический помощник разработчика[/bold blue]")
        console.print("[bold blue]════════════════════════════════════════════════════════════[/bold blue]")

    def print_success_message(self) -> None:
        """Печать сообщения об успешном завершении"""
        console.print(f"\n[green]🎉 Настройка DonutBuffer AI Wizard завершена успешно![/green]")
        console.print(f"[cyan]💡 Интеграция с GitHub настроена. Теперь вы можете:[/cyan]")
        console.print(f"   • Анализировать производительность ring buffer")
        console.print(f"   • Отслеживать падения тестов в CI/CD")
        console.print(f"   • Получать рекомендации по оптимизации C++ кода")
        console.print(f"   • Мониторить GitHub Actions и Pull Requests")
        console.print(f"\n[bold]🚀 AI-powered анализ DonutBuffer готов к работе![/bold]")

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