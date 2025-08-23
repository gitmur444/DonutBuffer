"""
🤖 Agent Injector - Инжекция промптов в cursor-agent

Отправляет автоматически сгенерированные промпты в cursor-agent.
"""

import subprocess
import time
from pathlib import Path
from typing import Optional
import sys
import os

# Импортируем из родительского пакета
sys.path.append(str(Path(__file__).parent.parent))
from core import BaseWizard

class AgentInjector(BaseWizard):
    """Инжектор промптов в cursor-agent"""
    
    def __init__(self):
        self.session_file = Path.home() / ".cursor" / "sessions" / "ambient.json"
        
    def inject_prompt(self, prompt: str, source: str = "ambient") -> bool:
        """
        Отправляет промпт в активную сессию cursor-agent (как от пользователя)
        
        Args:
            prompt: Текст промпта для отправки
            source: Источник промпта (для логирования)
            
        Returns:
            bool: Успешность отправки
        """
        self.print_info(f"🤖 [{source}] Отправляю в cursor-agent...")
        
        try:
            # Отправляем через CLI в активную сессию (без моста)
            result = subprocess.run([
                "cursor-agent", 
                prompt,  # Без префиксов - как будто пользователь написал
                "--print"
            ], 
            capture_output=True, 
            text=True, 
            timeout=30
            )
            
            if result.returncode == 0:
                self.print_success(f"✅ Промпт отправлен в cursor-agent")
                return True
            else:
                self.print_warning(f"CLI ошибка: {result.stderr}")
                return self.try_resume_method(prompt, source)
                
        except subprocess.TimeoutExpired:
            self.print_warning("Timeout при отправке через CLI")
            return self.try_resume_method(prompt, source)
        except Exception as e:
            self.print_warning(f"Ошибка CLI: {e}")
            return self.try_resume_method(prompt, source)
    
    def try_resume_method(self, prompt: str, source: str) -> bool:
        """Пытается найти активную сессию и отправить туда"""
        try:
            # Получаем список сессий
            result = subprocess.run([
                "cursor-agent", "ls"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                # Если есть сессии, попробуем отправить в последнюю
                self.print_info("🔄 Пытаюсь отправить в последнюю сессию...")
                result = subprocess.run([
                    "cursor-agent", "resume", 
                    prompt
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    self.print_success("✅ Промпт отправлен через resume")
                    return True
            
            # Если не удалось - fallback
            return self.fallback_to_file_injection(prompt, source)
            
        except Exception as e:
            self.print_warning(f"Ошибка resume: {e}")
            return self.fallback_to_file_injection(prompt, source)
    
    def fallback_to_file_injection(self, prompt: str, source: str) -> bool:
        """
        Fallback: сохраняет промпт в файл для ручного просмотра
        """
        try:
            ambient_dir = Path.home() / ".cursor" / "ambient"
            ambient_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = int(time.time())
            prompt_file = ambient_dir / f"{source}_{timestamp}.md"
            
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(f"# 🤖 Ambient Agent Notification\n\n")
                f.write(f"**Time:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"{prompt}\n\n")
                f.write("---\n*Copy this message and paste into cursor-agent*\n")
            
            self.print_warning(f"💾 Сообщение сохранено: {prompt_file}")
            self.print_info("💡 Скопируйте содержимое файла в cursor-agent")
            return True
            
        except Exception as e:
            self.print_error(f"Ошибка сохранения в файл: {e}")
            return False
    
    def inject_background_analysis(self, analysis_data: dict) -> bool:
        """
        Отправляет фоновый анализ в cursor-agent
        
        Args:
            analysis_data: Данные для анализа (тесты, логи, коммиты и т.д.)
        """
        
        # Формируем структурированный промпт
        prompt_parts = [
            "🔍 **ФОНОВЫЙ АНАЛИЗ DONUTBUFFER**",
            ""
        ]
        
        if "failed_tests" in analysis_data:
            prompt_parts.extend([
                "**Упавшие тесты:**",
                f"```",
                analysis_data["failed_tests"],
                f"```",
                ""
            ])
        
        if "logs" in analysis_data:
            prompt_parts.extend([
                "**Логи ошибок:**", 
                f"```",
                analysis_data["logs"][:1000] + "..." if len(analysis_data["logs"]) > 1000 else analysis_data["logs"],
                f"```",
                ""
            ])
            
        if "commits" in analysis_data:
            prompt_parts.extend([
                "**Последние коммиты:**",
                analysis_data["commits"],
                ""
            ])
        
        prompt_parts.extend([
            "**Задача:** Проанализируй причины проблем и предложи решения.",
            "Фокусируйся на C++ ring buffer, производительности и lockfree vs mutex."
        ])
        
        prompt = "\n".join(prompt_parts)
        return self.inject_prompt(prompt, "github_monitor")
    
    def check_cursor_agent_availability(self) -> bool:
        """Проверяет доступность cursor-agent"""
        try:
            result = subprocess.run(
                ["cursor-agent", "--help"], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        except:
            return False 