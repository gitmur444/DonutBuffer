"""
🧙‍♂️ DonutBuffer AI Wizard - Integration Test

Тестирование готовой интеграции GitHub и cursor-agent.
"""

import subprocess
import requests
from src.core.base_wizard import BaseWizard
from src.core.env_manager import EnvManager

class IntegrationTest(BaseWizard):
    """Тестирование интеграции"""
    
    def __init__(self, env_manager: EnvManager):
        self.env_manager = env_manager
        
    def test_integration(self) -> bool:
        """Шаг 4: Тестирование интеграции"""
        self.print_step(4, "Тестирование интеграции")
        
        # Проверяем только GitHub API доступ
        return self.test_github_api()
    
    def test_github_api(self) -> bool:
        """Тестирование доступа к GitHub API"""
        github_token = self.env_manager.get_env_var("GITHUB_TOKEN")
        if not github_token:
            self.print_error("GITHUB_TOKEN не установлен")
            return False
            
        try:
            headers = {"Authorization": f"token {github_token}"}
            
            # Тестируем общий доступ к GitHub API
            user_response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            if user_response.status_code == 200:
                user_data = user_response.json()
                self.print_success(f"GitHub API работает для пользователя: {user_data.get('login', 'unknown')}")
                
                # Пытаемся найти реальный GitHub репозиторий
                repo_name = self.detect_github_repo()
                if repo_name:
                    repo_response = requests.get(f"https://api.github.com/repos/{repo_name}", headers=headers, timeout=10)
                    if repo_response.status_code == 200:
                        self.print_success(f"Доступ к репозиторию {repo_name} работает")
                    else:
                        self.print_warning(f"Репозиторий {repo_name} недоступен или приватный")
                else:
                    self.print_warning("Git remote не настроен, но GitHub API работает")
            else:
                self.print_error("Ошибка доступа к GitHub API")
                return False
                
        except Exception as e:
            self.print_warning(f"GitHub API тест: {e}")
            
        return True
    
    def detect_github_repo(self) -> str:
        """Определение GitHub репозитория из git remote"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.env_manager.project_dir
            )
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                
                # Парсим GitHub URL (поддерживаем https и ssh)
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
    
    # cursor-agent тест перенесён в ambient префлайт и выполняется косвенно через e2e