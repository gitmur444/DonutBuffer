"""
🧙‍♂️ DonutBuffer AI Wizard - Environment Manager

Управление переменными окружения и .env файлами.
"""

import os
from pathlib import Path
from .base import BaseWizard

class EnvManager(BaseWizard):
    """Менеджер для работы с .env файлами и переменными окружения"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.env_file = project_dir / ".env"
        
    def load_env_file(self) -> None:
        """Загрузка переменных из .env файла"""
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Убираем кавычки если есть
                        value = value.strip('"\'')
                        os.environ[key] = value

    def save_env_file(self, key: str, value: str) -> None:
        """Сохранение переменной в .env файл"""
        env_content = []
        key_updated = False
        
        # Читаем существующий файл если есть
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line_strip = line.strip()
                    if line_strip.startswith(f"{key}="):
                        env_content.append(f"{key}=\"{value}\"\n")
                        key_updated = True
                    else:
                        env_content.append(line)
        
        # Добавляем новый ключ если не нашли
        if not key_updated:
            env_content.append(f"{key}=\"{value}\"\n")
        
        # Записываем файл
        with open(self.env_file, 'w') as f:
            f.writelines(env_content)
        
        self.ensure_gitignore()

    def ensure_gitignore(self) -> None:
        """Убеждаемся что .env файл в .gitignore"""
        gitignore_file = self.project_dir / ".gitignore"
        
        # Проверяем есть ли .env в .gitignore
        gitignore_content = ""
        if gitignore_file.exists():
            with open(gitignore_file, 'r') as f:
                gitignore_content = f.read()
        
        if ".env" not in gitignore_content:
            # Добавляем .env в .gitignore
            with open(gitignore_file, 'a') as f:
                if gitignore_content and not gitignore_content.endswith('\n'):
                    f.write('\n')
                f.write('# Environment variables\n.env\n')

    def get_env_var(self, key: str, default: str = None) -> str:
        """Получение переменной окружения"""
        return os.getenv(key, default) 