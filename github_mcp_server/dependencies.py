"""
🧙‍♂️ DonutBuffer AI Wizard - Dependencies Checker

Проверка зависимостей и установка Python пакетов.
"""

import sys
import subprocess
from core import BaseWizard

class DependencyChecker(BaseWizard):
    """Проверка и установка зависимостей"""
    
    def check_dependencies(self) -> bool:
        """Шаг 1: Проверка зависимостей"""
        self.print_step(1, "Проверка зависимостей")
        
        dependencies = {
            'git': 'Git для работы с репозиторием',
            'python3': 'Python 3 для скриптов',
            'node': 'Node.js для MCP серверов', 
            'cursor-agent': 'Cursor Agent CLI'
        }
        
        all_good = True
        for cmd, desc in dependencies.items():
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    version = result.stdout.strip().split('\n')[0]
                    self.print_success(f"{cmd}: {version}")
                else:
                    self.print_error(f"{cmd} не найден - {desc}")
                    all_good = False
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.print_error(f"{cmd} не найден - {desc}")
                if cmd == 'cursor-agent':
                    self.print_warning("Установите Cursor Agent: curl https://cursor.com/install -fsSL | bash")
                all_good = False
        
        # Проверяем Python пакеты
        self.check_python_packages()
            
        return all_good

    def check_python_packages(self) -> None:
        """Проверка и установка Python пакетов"""
        try:
            import requests
            self.print_success("Python requests модуль доступен")
        except ImportError:
            self.print_warning("Устанавливаю requests...")
            subprocess.run([sys.executable, "-m", "pip", "install", "requests"]) 