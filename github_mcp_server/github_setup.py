"""
🧙‍♂️ DonutBuffer AI Wizard - GitHub Setup

Настройка GitHub токена и проверка доступа к API.
"""

import getpass
import requests
from core import BaseWizard, Colors
from env_manager import EnvManager

class GitHubSetup(BaseWizard):
    """Настройка GitHub интеграции"""
    
    def __init__(self, env_manager: EnvManager):
        self.env_manager = env_manager
        
    def setup_github_token(self) -> bool:
        """Шаг 2: Настройка GitHub токена"""
        self.print_step(2, "Настройка GitHub токена")
        
        # Проверяем существующий токен (из .env или переменных окружения)
        github_token = self.env_manager.get_env_var("GITHUB_TOKEN")
        if github_token:
            # Проверяем валидность токена
            if self.validate_token(github_token):
                # Убеждаемся что токен сохранен в .env файле
                if not self.env_manager.env_file.exists() or f'GITHUB_TOKEN="{github_token}"' not in self.env_manager.env_file.read_text():
                    self.env_manager.save_env_file("GITHUB_TOKEN", github_token)
                    self.print_success("Токен сохранен в .env файл")
                return True
            else:
                self.print_warning("Существующий GitHub токен недействителен")
        
        # Запрашиваем новый токен
        return self.request_new_token()
    
    def validate_token(self, token: str) -> bool:
        """Проверка валидности GitHub токена"""
        try:
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                self.print_success(f"GitHub токен валиден для пользователя: {user_data.get('login', 'unknown')}")
                return True
            else:
                return False
        except Exception as e:
            self.print_warning(f"Ошибка проверки токена: {e}")
            return False
    
    def request_new_token(self) -> bool:
        """Запрос нового GitHub токена"""
        print(f"\n{Colors.YELLOW}📋 Создайте GitHub Personal Access Token:{Colors.NC}")
        print("1. Перейдите: https://github.com/settings/tokens")
        print("2. Нажмите 'Generate new token' → 'Generate new token (classic)'")
        print("3. Выберите scopes: repo, workflow, read:org")
        print("4. Скопируйте созданный токен\n")
        
        token = getpass.getpass("🔑 Введите GitHub токен: ").strip()
        if not token:
            self.print_error("Токен не может быть пустым")
            return False
            
        # Проверяем новый токен
        try:
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                self.print_success(f"Токен валиден для пользователя: {user_data.get('login', 'unknown')}")
                
                # Сохраняем в переменные окружения для текущей сессии
                import os
                os.environ["GITHUB_TOKEN"] = token
                
                # Сохраняем в .env файл для постоянного использования
                self.env_manager.save_env_file("GITHUB_TOKEN", token)
                self.print_success(f"Токен сохранен в {self.env_manager.env_file.name}")
                self.print_warning("⚠️  Файл .env автоматически добавлен в .gitignore для безопасности")
                
                return True
            else:
                self.print_error("Недействительный GitHub токен")
                return False
        except Exception as e:
            self.print_error(f"Ошибка проверки токена: {e}")
            return False 