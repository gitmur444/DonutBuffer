"""
💬 Prompt Generator - Упрощённый: только анализ упавшей CI джобы

Генерирует промпт ТОЛЬКО для событий workflow, завершившихся с ошибкой.
Все остальные типы событий возвращают пустую строку.
"""

import time
from typing import Dict, Any, List
import sys
from pathlib import Path

# Импортируем из родительского пакета
sys.path.append(str(Path(__file__).parent.parent))
from ..core.base_wizard import BaseWizard
from .event_system import Event, EventType

class PromptGenerator(BaseWizard):
    """Генератор промптов: только для упавших workflow."""
    
    def generate_prompt(self, event: Event) -> str:
        """Возвращает текст промпта или пустую строку, если промпт не нужен."""
        if event.type != EventType.GITHUB_WORKFLOW_EVENT:
            return ""
        return self.generate_workflow_event_prompt(event)
    
    def generate_workflow_event_prompt(self, event: Event) -> str:
        """Промпт ТОЛЬКО для упавших workflow (conclusion == failure)."""
        data = event.data
        conclusion = str(data.get("conclusion") or "").lower()
        if conclusion not in ("failure", "failed", "cancelled"):
            return ""

        workflow_name = data.get("workflow_name", "Unknown")
        run_number = data.get("run_number", "?")
        html_url = data.get("html_url", "")
        head = data.get("head_commit", {}) or {}
        commit_author = (head.get("author") or {}).get("name") or head.get("author", "?")
        commit_message = head.get("message", "")
        commit_sha = head.get("id", "")[:7]

        return (
            "🛠️ Сборка/тесты упали\n\n"
            f"Workflow: {workflow_name} (Run #{run_number})\n"
            f"URL: {html_url}\n\n"
            "Последний коммит:\n"
            f"- Автор: {commit_author}\n"
            f"- Сообщение: {commit_message}\n"
            f"- SHA: {commit_sha}\n\n"
            "Задача: определи причину падения и предложи исправления."
        )
    
    # Остальные генераторы больше не используются. Возвращаем пустые строки.
    def generate_pr_analysis_prompt(self, event: Event) -> str:
        return ""
    
    def generate_manual_analysis_prompt(self, event: Event) -> str:
        return ""
    
    def generate_generic_prompt(self, event: Event) -> str:
        return ""
    
    def extract_repo_name(self, data: Dict) -> str:
        """Извлекает имя репозитория из данных"""
        # Попытаемся извлечь из URL
        html_url = data.get("html_url", "")
        if "github.com" in html_url:
            parts = html_url.split("/")
            if len(parts) >= 5:
                return f"{parts[-4]}/{parts[-3]}"
        
        return "DonutBuffer"
    
    def format_timestamp(self, timestamp: float) -> str:
        """Форматирует временную метку"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    
    def format_event_data(self, data: Dict[str, Any]) -> str:
        """Форматирует данные события для отображения"""
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"{key}:")
                for subkey, subvalue in value.items():
                    lines.append(f"  {subkey}: {subvalue}")
            elif isinstance(value, list):
                lines.append(f"{key}: {len(value)} items")
            else:
                # Ограничиваем длинные значения
                str_value = str(value)
                if len(str_value) > 200:
                    str_value = str_value[:200] + "..."
                lines.append(f"{key}: {str_value}")
        
        return "\n".join(lines)
    
    def create_custom_prompt(self, analysis_type: str, content: str, focus_areas: List[str] = None) -> str:
        return ""
    
    def generate_test_issue_prompt(self, event: Event) -> str:
        return ""