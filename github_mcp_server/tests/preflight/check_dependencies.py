from pathlib import Path
import subprocess
import sys

from src.core.base_wizard import BaseWizard
from src.core.env_manager import EnvManager


def run_dependencies_check(donut_dir: Path) -> tuple[bool, str]:
    env = EnvManager(donut_dir)
    env.load_env_file()

    printer = BaseWizard()
    printer.print_step(1, "Проверка зависимостей")

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
                version = (result.stdout or result.stderr).strip().split('\n')[0]
                printer.print_success(f"{cmd}: {version}")
            else:
                printer.print_error(f"{cmd} не найден - {desc}")
                all_good = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            printer.print_error(f"{cmd} не найден - {desc}")
            if cmd == 'cursor-agent':
                printer.print_warning("Установите Cursor Agent: curl https://cursor.com/install -fsSL | bash")
            all_good = False

    # Проверяем Python пакеты
    try:
        import requests  # noqa: F401
        printer.print_success("Python requests модуль доступен")
    except ImportError:
        printer.print_warning("Устанавливаю requests...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"])  # best-effort

    return all_good, "dependencies: ok" if all_good else "dependencies: fail"


