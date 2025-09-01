"""
🔍 GitHub Monitor - Мониторинг изменений в GitHub

Отслеживает падения тестов, изменения в репозитории и другие события.
"""

import requests
import time
import threading
from typing import Dict, List, Optional, Set
import sys
from pathlib import Path

# Импортируем из родительского пакета
sys.path.append(str(Path(__file__).parent.parent))
from ..core.base_wizard import BaseWizard
from ..core.env_manager import EnvManager
from .event_system import EventSystem, EventType

class GitHubMonitor(BaseWizard):
    """Мониторинг GitHub репозитория"""
    
    def __init__(self, event_system: EventSystem, env_manager: EnvManager):
        self.event_system = event_system
        self.env_manager = env_manager
        self.github_token = env_manager.get_env_var("GITHUB_TOKEN")
        self.repo_name = self.detect_repo_name()
        
        # Состояние мониторинга
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_check_time = time.time()
        self.seen_runs: Set[str] = set()
        self.seen_failures: Set[str] = set()
        self.start_time = time.time()
        
        # Настройки
        self.check_interval = 10  # быстрее реагируем
        
    def detect_repo_name(self) -> Optional[str]:
        """Определяет имя GitHub репозитория"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                
                if "github.com" in remote_url:
                    if remote_url.startswith("git@github.com:"):
                        # SSH format: git@github.com:user/repo.git
                        repo_part = remote_url.split(":")[-1].replace(".git", "")
                        return repo_part
                    elif "github.com/" in remote_url:
                        # HTTPS format: https://github.com/user/repo.git
                        repo_part = remote_url.split("github.com/")[-1].replace(".git", "")
                        return repo_part
        except:
            pass
        return None
    
    def start_monitoring(self) -> bool:
        """Запускает мониторинг GitHub"""
        if not self.github_token:
            self.print_error("GitHub токен не найден")
            return False
            
        if not self.repo_name:
            self.print_warning("Имя репозитория не определено, мониторинг ограничен")
        
        if self.monitoring:
            self.print_warning("Мониторинг уже запущен")
            return True
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self.monitoring_loop,
            daemon=True
        )
        # Перед запуском — запоминаем текущие ранны, чтобы не слать историю
        try:
            self._baseline_runs()
        except Exception:
            pass
        self.monitor_thread.start()
        return True
    
    def stop_monitoring(self) -> None:
        """Останавливает мониторинг"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
    
    def monitoring_loop(self) -> None:
        """Основной цикл мониторинга"""
        while self.monitoring:
            try:
                # Проверяем workflow runs (GitHub Actions)
                self.check_workflow_runs()
                
                # Проверяем pull requests
                self.check_pull_requests()
                
                # Обновляем время последней проверки
                self.last_check_time = time.time()
                
                # Ожидаем до следующей проверки
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.print_error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(30)  # Пауза при ошибке
    
    def check_workflow_runs(self) -> None:
        """Проверяет workflow runs на наличие изменений"""
        if not self.repo_name:
            self.print_warning("[monitor] repo_name not detected, skip runs")
            return
            
        try:
            headers = {"Authorization": f"token {self.github_token}"}
            
            # Получаем недавние workflow runs (все статусы)
            url = f"https://api.github.com/repos/{self.repo_name}/actions/runs"
            params = {
                "per_page": 5,
                # Без фильтра по статусу - получаем все изменения
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code != 200:
                self.print_warning(f"Ошибка получения workflow runs: {response.status_code}")
                return
                
            data = response.json()
            
            for run in data.get("workflow_runs", []):
                run_id = str(run.get("id"))
                if not run_id:
                    continue
                status = run.get("status")
                conclusion = run.get("conclusion")
                # Новые ранны: queued/in_progress — считаем стартом
                if run_id not in self.seen_runs:
                    if status in ("queued", "in_progress") and not conclusion:
                        self.handle_workflow_event(run)
                    # Помечаем как увиденный, чтобы не слать историю
                    self.seen_runs.add(run_id)
                # Детект завершения с ошибкой (emit один раз на факт фейла)
                if str(conclusion).lower() in ("failure", "failed", "cancelled") and run_id not in self.seen_failures:
                    self.handle_workflow_event(run)
                    self.seen_failures.add(run_id)
                    
        except Exception as e:
            self.print_warning(f"Ошибка проверки workflow runs: {e}")
    
    def handle_workflow_event(self, run: Dict) -> None:
        """Обрабатывает событие workflow run"""
        status = run.get("status")
        conclusion = run.get("conclusion")
        # no debug prints here
        
        # Определяем тип события
        if status == "in_progress" or status == "queued":
            event_type = "запущен"
        else:
            event_type = f"изменился ({status})"
        
        # Формируем данные события
        event_data = {
            "run_id": run["id"],
            "run_number": run["run_number"], 
            "workflow_name": run["name"],
            "status": status,
            "conclusion": conclusion,
            "event_type": event_type,
            "html_url": run["html_url"],
            "head_commit": run.get("head_commit", {})
        }
        
        # Генерируем событие
        self.event_system.emit_simple(
            event_type=EventType.GITHUB_WORKFLOW_EVENT,
            data=event_data,
            source="github_monitor",
            priority=3
        )
        # no debug prints on emit

    
    def check_pull_requests(self) -> None:
        """Проверяет новые pull requests"""
        if not self.repo_name:
            return
            
        try:
            headers = {"Authorization": f"token {self.github_token}"}
            
            url = f"https://api.github.com/repos/{self.repo_name}/pulls"
            params = {
                "state": "open",
                "sort": "created",
                "direction": "desc",
                "per_page": 5
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code != 200:
                return
                
            data = response.json()
            
            for pr in data:
                pr_created = pr["created_at"]
                
                # Проверяем только недавно созданные PR
                # (простая проверка по времени)
                if self.is_recent_pr(pr_created):
                    event_data = {
                        "pr_number": pr["number"],
                        "pr_title": pr["title"],
                        "pr_url": pr["html_url"],
                        "author": pr["user"]["login"],
                        "created_at": pr_created
                    }
                    
                    self.event_system.emit_simple(
                        event_type=EventType.GITHUB_PR_CREATED,
                        data=event_data,
                        source="github_monitor",
                        priority=2
                    )
                    
        except Exception as e:
            self.print_warning(f"Ошибка проверки PR: {e}")
    
    def is_recent_pr(self, created_at: str) -> bool:
        """Проверяет, является ли PR недавно созданным"""
        try:
            from datetime import datetime, timezone
            
            # Парсим время создания PR
            pr_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            now = datetime.now(timezone.utc)
            
            # Считаем недавними PR созданные за последние 2 часа
            diff = (now - pr_time).total_seconds()
            return diff < 7200  # 2 часа
            
        except:
            return False
    
    def manual_check(self) -> Dict:
        """Ручная проверка состояния репозитория"""
        result = {
            "repo_name": self.repo_name,
            "monitoring_active": self.monitoring,
            "last_check": self.last_check_time,
            "seen_runs": len(self.seen_runs)
        }
        return result
    
    def get_headers(self) -> Dict[str, str]:
        """Возвращает заголовки для GitHub API"""
        return {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "DonutBuffer-Ambient-Agent"
        }
    
    def create_test_issue(self) -> Dict:
        """Создает тестовый issue для E2E проверки"""
        import time
        
        if not self.repo_name:
            raise Exception("Repo name not detected")
        
        url = f"https://api.github.com/repos/{self.repo_name}/issues"
        timestamp = int(time.time())
        
        data = {
            "title": f"[AMBIENT-TEST] System check {timestamp}",
            "body": "Auto-generated test issue for ambient agent E2E testing",
            "labels": ["ambient-test", "auto-generated"]
        }
        
        response = requests.post(url, json=data, headers=self.get_headers())
        if not response.ok:
            raise Exception(f"Failed to create test issue: {response.status_code}")
        
        return response.json()
    
    def delete_test_issue(self, issue_number: int) -> None:
        """Закрывает тестовый issue"""
        if not self.repo_name:
            raise Exception("Repo name not detected")
        
        # 1. Добавляем комментарий о завершении теста
        comment_url = f"https://api.github.com/repos/{self.repo_name}/issues/{issue_number}/comments"
        comment_data = {
            "body": "✅ E2E test completed successfully. Closing automatically."
        }
        
        response = requests.post(comment_url, json=comment_data, headers=self.get_headers())
        if not response.ok:
            raise Exception(f"Failed to add cleanup comment: {response.status_code}")
        
        # 2. Закрываем issue
        issue_url = f"https://api.github.com/repos/{self.repo_name}/issues/{issue_number}"
        close_data = {
            "state": "closed"
        }
        
        response = requests.patch(issue_url, json=close_data, headers=self.get_headers())
        if not response.ok:
            raise Exception(f"Failed to close issue: {response.status_code}")
    
    def check_for_test_issues(self, specific_issue_number: int = None) -> None:
        """Проверяет наличие тестовых issues и генерирует события"""
        if not self.repo_name:
            return
        
        if specific_issue_number:
            # Проверяем конкретный issue
            url = f"https://api.github.com/repos/{self.repo_name}/issues/{specific_issue_number}"
            
            try:
                response = requests.get(url, headers=self.get_headers())
                if not response.ok:
                    return
                
                issue = response.json()
                
                # Проверяем что это наш тестовый issue (и он открыт - только что созданный)
                if "[AMBIENT-TEST]" in issue["title"] and issue["state"] == "open" and "ambient-test" in [label["name"] for label in issue.get("labels", [])]:
                    self.event_system.emit_simple(
                        event_type=EventType.GITHUB_ISSUE_TEST,
                        source="github_monitor",
                        data={
                            "issue_number": issue["number"],
                            "title": issue["title"],
                            "created_at": issue["created_at"]
                        }
                    )
                    
            except Exception as e:
                self.print_warning(f"Ошибка проверки issue #{specific_issue_number}: {e}")
        else:
            # Старая логика - ищем все тестовые issues (для общего мониторинга)
            url = f"https://api.github.com/repos/{self.repo_name}/issues"
            params = {
                "labels": "ambient-test",
                "state": "all",
                "per_page": 10
            }
            
            try:
                response = requests.get(url, params=params, headers=self.get_headers())
                if not response.ok:
                    return
                
                issues = response.json()
                
                for issue in issues:
                    if "[AMBIENT-TEST]" in issue["title"]:
                        self.event_system.emit_simple(
                            event_type=EventType.GITHUB_ISSUE_TEST,
                            source="github_monitor",
                            data={
                                "issue_number": issue["number"],
                                "title": issue["title"],
                                "created_at": issue["created_at"]
                            }
                        )
                        
            except Exception as e:
                self.print_warning(f"Ошибка проверки тестовых issues: {e}")
    
    def force_check(self, specific_issue_number: int = None) -> None:
        """Принудительная проверка GitHub без ожидания таймера"""
        self.check_for_test_issues(specific_issue_number) 

    def _baseline_runs(self) -> None:
        """Помечает текущие workflow runs как уже увиденные, чтобы не слать историю."""
        if not self.repo_name:
            return
        headers = {"Authorization": f"token {self.github_token}"}
        url = f"https://api.github.com/repos/{self.repo_name}/actions/runs"
        params = {"per_page": 10}
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if not resp.ok:
            return
        data = resp.json()
        for run in data.get("workflow_runs", []):
            run_id = str(run.get("id"))
            if run_id:
                self.seen_runs.add(run_id)
                conclusion = str(run.get("conclusion") or "").lower()
                if conclusion in ("failure", "failed", "cancelled"):
                    # Не слать событий на старые фейлы
                    self.seen_failures.add(run_id)