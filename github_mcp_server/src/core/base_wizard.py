"""
🧙‍♂️ DonutBuffer AI Wizard - Core Module

Базовые классы и утилиты для DonutBuffer AI Wizard.
"""

from rich.console import Console

console = Console()

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
        console.print(f"\n[cyan]🔮 Шаг {step}/6: [bold]{message}[/bold][/cyan]")
        
    def print_success(self, message: str) -> None:
        """Print success message."""
        console.print(f"[green]✅ {message}[/green]")
        
    def print_error(self, message: str) -> None:
        """Print error message."""
        console.print(f"[red]❌ {message}[/red]")
        
    def print_warning(self, message: str) -> None:
        """Print warning message."""
        console.print(f"[yellow]⚠️  {message}[/yellow]")

    def print_info(self, message: str) -> None:
        """Print info message."""
        console.print(f"[blue]ℹ️  {message}[/blue]")