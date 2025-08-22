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
            # Выполняем все 4 шага
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
            
            # Настройка завершена успешно
            self._print_success_message()
            
            # Запускаем cursor-agent
            self._launch_cursor_agent()
            
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
        """Запуск cursor-agent с приветственным сообщением"""
        
        # Формируем стартовый промпт
        startup_prompt = (
            "GitHub интеграция настроена. Доступные сценарии:\n"
            "• Анализ производительности lockfree vs mutex\n"
            "• Диагностика упавших тестов в CI/CD\n"
            "• Оптимизация C++ ring buffer\n"
            "• Мониторинг GitHub Actions\n"
            "Что анализируем?"
        )
        
        try:
            # Запускаем cursor-agent с приветственным сообщением
            import subprocess
            subprocess.run([
                "cursor-agent", "chat", startup_prompt
            ])
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}👋 До встречи! Используйте 'cursor-agent' для продолжения работы.{Colors.NC}")
        except Exception as e:
            self.print_error(f"Ошибка запуска cursor-agent: {e}")
            print(f"{Colors.CYAN}💡 Запустите вручную: cursor-agent{Colors.NC}")

if __name__ == "__main__":
    wizard = DonutAIWizard()
    wizard.run() 