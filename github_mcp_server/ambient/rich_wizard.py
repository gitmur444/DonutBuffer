"""
Rich-powered wizard output - beautiful tables and panels for setup steps
"""

import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.align import Align
import time

console = Console()


class RichWizard:
    """Rich-powered wizard for beautiful output"""
    
    def __init__(self):
        self.console = console
        
    def print_header(self):
        """Print beautiful header"""
        header_text = Text()
        header_text.append("🧙‍♂️ ", style="bold blue")
        header_text.append("DonutBuffer AI Wizard", style="bold white")
        header_text.append(" - Магический помощник разработчика", style="dim white")
        
        panel = Panel(
            Align.center(header_text),
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
        self.console.print()

    def print_step_start(self, step: int, title: str, description: str = ""):
        """Start a step with beautiful formatting"""
        step_text = Text()
        step_text.append(f"🔮 Шаг {step}/5: ", style="bold cyan")
        step_text.append(title, style="bold white")
        
        if description:
            step_text.append(f"\n{description}", style="dim white")
        
        panel = Panel(
            step_text,
            border_style="cyan",
            padding=(0, 1)
        )
        
        self.console.print(panel)

    def print_step_progress(self, message: str, is_success: bool = None):
        """Print step progress"""
        if is_success is True:
            self.console.print(f"✅ {message}", style="bold green")
        elif is_success is False:
            self.console.print(f"❌ {message}", style="bold red")
        else:
            self.console.print(f"🔄 {message}", style="yellow")

    def print_success_summary(self):
        """Print final success summary"""
        
        # Create summary table
        table = Table(title="🎉 Настройка завершена успешно!", title_style="bold green")
        table.add_column("Компонент", style="cyan", width=20)
        table.add_column("Статус", style="green", width=10)
        table.add_column("Описание", style="white")
        
        table.add_row("Dependencies", "✅ OK", "Все зависимости установлены")
        table.add_row("GitHub Token", "✅ OK", "API токен настроен и проверен")
        table.add_row("MCP Server", "✅ OK", "GitHub MCP Server готов")
        table.add_row("Integration", "✅ OK", "Тестирование прошло успешно")
        table.add_row("Ambient Agent", "✅ OK", "Система событий работает")
        
        self.console.print()
        self.console.print(table)
        
        # Features panel
        features_text = Text()
        features_text.append("💡 Теперь вы можете:\n", style="bold cyan")
        features_text.append("• Анализировать производительность ring buffer\n", style="white")
        features_text.append("• Отслеживать падения тестов в CI/CD\n", style="white")
        features_text.append("• Получать рекомендации по оптимизации C++ кода\n", style="white")
        features_text.append("• Мониторить GitHub Actions и Pull Requests", style="white")
        
        features_panel = Panel(
            features_text,
            title="Возможности",
            title_align="left",
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(features_panel)

    def print_error(self, message: str):
        """Print error message"""
        error_panel = Panel(
            f"❌ {message}",
            border_style="red",
            padding=(0, 1)
        )
        self.console.print(error_panel)

    def print_warning(self, message: str):
        """Print warning message"""
        warning_panel = Panel(
            f"⚠️  {message}",
            border_style="yellow",
            padding=(0, 1)
        )
        self.console.print(warning_panel)

    def show_launch_message(self):
        """Show launch message before starting interactive UI"""
        launch_text = Text()
        launch_text.append("🚀 ", style="bold green")
        launch_text.append("AI-powered анализ DonutBuffer готов к работе!", style="bold white")
        launch_text.append("\n\nЗапускаю интерактивный режим...", style="dim white")
        
        panel = Panel(
            Align.center(launch_text),
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print()
        self.console.print(panel)
        self.console.print()
        
        # Small delay for effect
        time.sleep(1)
