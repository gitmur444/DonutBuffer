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
from core import BaseWizard
from env_manager import EnvManager
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
        self.known_failures: Set[str] = set()
        
        # Настройки
        self.check_interval = 60  # секунд между проверками
        
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
        self.monitor_thread.start()
        
        self.print_success(f"🔍 GitHub мониторинг запущен (repo: {self.repo_name or 'unknown'})")
        return True
    
    def stop_monitoring(self) -> None:
        """Останавливает мониторинг"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        self.print_info("🔍 GitHub мониторинг остановлен")
    
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
        """Проверяет workflow runs на наличие падений"""
        if not self.repo_name:
            return
            
        try:
            headers = {"Authorization": f"token {self.github_token}"}
            
            # Получаем недавние workflow runs
            url = f"https://api.github.com/repos/{self.repo_name}/actions/runs"
            params = {
                "per_page": 10,
                "status": "completed"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code != 200:
                self.print_warning(f"Ошибка получения workflow runs: {response.status_code}")
                return
                
            data = response.json()
            
            for run in data.get("workflow_runs", []):
                run_id = str(run["id"])
                conclusion = run.get("conclusion")
                
                # Проверяем на неудачные runs
                if conclusion == "failure" and run_id not in self.known_failures:
                    self.known_failures.add(run_id)
                    
                    # Получаем детали об ошибке
                    self.handle_workflow_failure(run)
                    
        except Exception as e:
            self.print_warning(f"Ошибка проверки workflow runs: {e}")
    
    def handle_workflow_failure(self, run: Dict) -> None:
        """Обрабатывает упавший workflow run"""
        self.print_warning(f"🚨 Упал workflow: {run['name']} (#{run['run_number']})")
        
        # Получаем логи
        logs = self.get_workflow_logs(run["id"])
        
        # Формируем данные события
        event_data = {
            "run_id": run["id"],
            "run_name": run["name"],
            "run_number": run["run_number"], 
            "workflow_name": run["name"],
            "conclusion": run["conclusion"],
            "html_url": run["html_url"],
            "head_commit": run.get("head_commit", {}),
            "logs": logs[:2000] if logs else "Логи недоступны"  # Ограничиваем размер
        }
        
        # Генерируем событие
        self.event_system.emit_simple(
            event_type=EventType.GITHUB_TEST_FAILED,
            data=event_data,
            source="github_monitor",
            priority=4  # Высокий приоритет
        )
    
    def get_workflow_logs(self, run_id: int) -> Optional[str]:
        """Получает логи workflow run"""
        try:
            headers = {"Authorization": f"token {self.github_token}"}
            
            # Получаем jobs для run
            jobs_url = f"https://api.github.com/repos/{self.repo_name}/actions/runs/{run_id}/jobs"
            jobs_response = requests.get(jobs_url, headers=headers, timeout=10)
            
            if jobs_response.status_code != 200:
                return None
                
            jobs_data = jobs_response.json()
            logs = []
            
            for job in jobs_data.get("jobs", []):
                if job.get("conclusion") == "failure":
                    logs.append(f"❌ Job: {job['name']}")
                    
                    for step in job.get("steps", []):
                        if step.get("conclusion") == "failure":
                            logs.append(f"  ❌ Step: {step['name']}")
                            
            return "\n".join(logs) if logs else None
            
        except Exception as e:
            self.print_warning(f"Ошибка получения логов: {e}")
            return None
    
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
            "known_failures": len(self.known_failures)
        }
        
        self.print_info(f"📊 Статус мониторинга: {result}")
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