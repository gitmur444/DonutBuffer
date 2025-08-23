"""
🧙‍♂️ DonutBuffer AI Wizard - Main Module

Главный модуль мастера настройки AI-анализа DonutBuffer проекта.
"""

from pathlib import Path
from core import BaseWizard, Colors
from env_manager import EnvManager
from dependencies import DependencyChecker
from github_setup import GitHubSetup
from mcp_setup import MCPSetup
from integration_test import IntegrationTest

# Импортируем Ambient Agent для тестирования
import sys
sys.path.append(str(Path(__file__).parent))
from ambient.ambient_agent import AmbientAgent
import threading

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
            # Выполняем все 5 шагов
            if not self.dependency_checker.check_dependencies():
                self.print_error("Установите недостающие зависимости и запустите снова")
                return
                
            if not self.github_setup.setup_github_token():
                self.print_error("Настройте GitHub токен и запустите снова")
                return
                
            if not self.mcp_setup.setup_github_mcp():
                self.print_error("Ошибка настройки MCP Server")
                return
                
            if not self.integration_test.test_integration():
                self.print_warning("Интеграция работает с предупреждениями")
            
            if not self.test_ambient_system():
                self.print_error("❌ E2E тест Ambient Agent провален!")
                self.print_error("Система неработоспособна. Cursor-agent НЕ будет запущен.")
                self.print_info("💡 Проверьте GitHub API доступность и повторите настройку")
                return
            
            # Настройка завершена успешно
            self.print_success_message()
            
            # Запускаем Ambient Agent в фоне и PTY bridge для cursor-agent
            # Запускаем AmbientAgent без регистрации SIGINT, чтобы Ctrl+C вернул в shell
            # При этом приглушим его собственный вывод, чтобы не мешал TUI
            import os
            # Делаем AmbientAgent полностью тихим на всё время работы, чтобы не дёргать TUI
            os.environ["AMBIENT_SILENT"] = "1"
            self.start_ambient_agent_background_no_sig()

            # Запускаем cursor-agent напрямую
            self.launch_cursor_agent()
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⚠️  Настройка прервана пользователем{Colors.NC}")
        except Exception as e:
            self.print_error(f"Неожиданная ошибка: {e}")

    def print_header(self) -> None:
        """Печать заголовка мастера"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("🧙‍♂️ ════════════════════════════════════════════════════════════")
        print("   DonutBuffer AI Wizard - Магический помощник разработчика")
        print("════════════════════════════════════════════════════════════")
        print(f"{Colors.NC}")

    def print_success_message(self) -> None:
        """Печать сообщения об успешном завершении"""
        print(f"\n{Colors.GREEN}🎉 Настройка DonutBuffer AI Wizard завершена успешно!{Colors.NC}")
        print(f"{Colors.CYAN}💡 Интеграция с GitHub настроена. Теперь вы можете:{Colors.NC}")
        print(f"   • Анализировать производительность ring buffer")
        print(f"   • Отслеживать падения тестов в CI/CD")
        print(f"   • Получать рекомендации по оптимизации C++ кода")
        print(f"   • Мониторить GitHub Actions и Pull Requests")
        print(f"\n{Colors.BOLD}🚀 AI-powered анализ DonutBuffer готов к работе!{Colors.NC}")

    def launch_cursor_agent(self) -> None:
        """Запуск cursor-agent без моста."""
        try:
            import subprocess
            subprocess.run(["cursor-agent"])  # обычный запуск
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}👋 До встречи! Используйте 'cursor-agent' для продолжения работы.{Colors.NC}")
        except Exception as e:
            self.print_error(f"Ошибка запуска cursor-agent: {e}")
            print(f"{Colors.CYAN}💡 Запустите вручную: cursor-agent{Colors.NC}")

    def start_ambient_agent_background_no_sig(self) -> None:
        """Стартует AmbientAgent в фоновом потоке без перехвата Ctrl+C."""
        try:
            import os, sys
            self._ambient = AmbientAgent(self.donut_dir, install_signal_handlers=False)

            def _runner():
                # Полностью подавляем вывод фонового агента, чтобы не мешать TUI
                devnull = None
                prev_out, prev_err = sys.stdout, sys.stderr
                try:
                    devnull = open(os.devnull, 'w')
                    sys.stdout = devnull
                    sys.stderr = devnull
                    self._ambient.start()
                finally:
                    try:
                        if devnull:
                            devnull.close()
                    except Exception:
                        pass
                    sys.stdout, sys.stderr = prev_out, prev_err

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

if __name__ == "__main__":
    wizard = DonutAIWizard()
    wizard.run() 