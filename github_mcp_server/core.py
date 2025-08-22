"""
🧙‍♂️ DonutBuffer AI Wizard - Core Module

Базовые классы и утилиты для DonutBuffer AI Wizard.
"""

class Colors:
    """ANSI цветовые коды для красивого вывода"""
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'

class BaseWizard:
    """Базовый класс с общими методами для всех компонентов мастера"""
    
    def print_step(self, step: int, message: str) -> None:
        """Print step with beautiful formatting."""
        print(f"\n{Colors.CYAN}🔮 Шаг {step}/4: {Colors.BOLD}{message}{Colors.NC}")
        
    def print_success(self, message: str) -> None:
        """Print success message."""
        print(f"{Colors.GREEN}✅ {message}{Colors.NC}")
        
    def print_error(self, message: str) -> None:
        """Print error message."""
        print(f"{Colors.RED}❌ {message}{Colors.NC}")
        
    def print_warning(self, message: str) -> None:
        """Print warning message."""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.NC}")

    def print_info(self, message: str) -> None:
        """Print info message."""
        print(f"{Colors.BLUE}ℹ️  {message}{Colors.NC}") 