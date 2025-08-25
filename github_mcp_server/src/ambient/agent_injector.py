"""
🤖 Agent Injector - Инжекция промптов в cursor-agent

Отправляет автоматически сгенерированные промпты в cursor-agent.
"""

import subprocess
import time
from pathlib import Path
from typing import Optional, Any
import sys
import os
import json

# Импортируем из родительского пакета
sys.path.append(str(Path(__file__).parent.parent))
from ..core.base_wizard import BaseWizard

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
            # Потоковый режим JSON, выводим сообщения пользователя в рамке
            return self._run_streaming(prompt)
        except subprocess.TimeoutExpired:
            self.print_warning("Timeout при отправке через CLI")
            return self.try_resume_method(prompt, source)
        except Exception as e:
            self.print_warning(f"Ошибка CLI: {e}")
            return self.try_resume_method(prompt, source)

    def _run_streaming(self, prompt: str) -> bool:
        """Запускает cursor-agent с --print --output-format stream-json и оформляет вывод.

        - Сообщения пользователя (role=user) печатаются один раз в рамке
        - Ответ ассистента стримится токенами без переноса строки, с принудительным flush
        - Итог (type=result) завершает строку
        """
        try:
            with subprocess.Popen(
                ["cursor-agent", prompt, "--print", "--output-format", "stream-json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            ) as proc:
                assert proc.stdout is not None
                printed_user = False
                for line in proc.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    # Пытаемся распарсить JSON-событие
                    obj: Any = None
                    try:
                        obj = json.loads(line)
                    except Exception:
                        # Некорректная строка — просто печатаем
                        print(line)
                        continue
                    # Пользовательское сообщение (один раз)
                    if not printed_user and self._is_user_event(obj):
                        content = self._extract_text(obj)
                        if content:
                            print(self._box(content))
                            printed_user = True
                        continue
                    # Поток ассистента — печатаем без перевода строки
                    if self._is_assistant_event(obj):
                        chunk = self._extract_text(obj)
                        if chunk:
                            print(chunk, end="", flush=True)
                        continue
                    # Финальный результат — перенос строки
                    if obj.get("type") == "result":
                        print("")
                        continue
                    # Остальное: игнорируем или печатаем компактно, если есть текст
                    text = self._extract_text(obj)
                    if text:
                        print(text)
                return proc.wait() == 0
        except Exception as e:
            self.print_warning(f"stream-json ошибка: {e}")
            return False

    def stream_with_callbacks(
        self,
        prompt: str,
        on_user: Optional[callable] = None,
        on_chunk: Optional[callable] = None,
        on_result: Optional[callable] = None,
    ) -> bool:
        """Стримит ответ агента, вызывая колбэки для UI.

        - on_user(text): один раз, когда зафиксировано сообщение пользователя
        - on_chunk(text): фрагменты ответа ассистента по мере поступления
        - on_result(full_or_final_line): финал запроса
        """
        try:
            with subprocess.Popen(
                ["cursor-agent", prompt, "--print", "--output-format", "stream-json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            ) as proc:
                assert proc.stdout is not None
                printed_user = False
                for line in proc.stdout:
                    line = line.strip()
                    if not line:
                        continue
                    obj: Any = None
                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue
                    if not printed_user and self._is_user_event(obj):
                        content = self._extract_text(obj)
                        if content and on_user:
                            on_user(content)
                        printed_user = True
                        continue
                    if self._is_assistant_event(obj):
                        chunk = self._extract_text(obj)
                        if chunk and on_chunk:
                            on_chunk(chunk)
                        continue
                    if isinstance(obj, dict) and obj.get("type") == "result":
                        if on_result:
                            on_result(obj.get("result") or "")
                        continue
                return proc.wait() == 0
        except Exception as e:
            self.print_warning(f"stream-json ошибка: {e}")
            return False

    def _try_print_user_message_box(self, obj: Any) -> bool:
        """Пробует найти {role:user, content:...} и вывести рамку. Возвращает True если напечатали."""
        # Прямой формат
        if isinstance(obj, dict):
            if obj.get("role") == "user":
                content = self._extract_text(obj)
                if content:
                    print(self._box(content))
                    return True
            # Поиск глубже
            for v in obj.values():
                if self._try_print_user_message_box(v):
                    return True
        elif isinstance(obj, list):
            for it in obj:
                if self._try_print_user_message_box(it):
                    return True
        return False

    def _extract_text(self, obj: Any) -> str:
        """Извлекает текст из объекта события максимально толерантно."""
        if isinstance(obj, dict):
            # cursor-agent stream-json: message.content: [{type:'text', text:'...'}]
            if isinstance(obj.get("message"), dict):
                return self._extract_text(obj["message"])
            if isinstance(obj.get("content"), str):
                return obj.get("content")
            if isinstance(obj.get("content"), list):
                parts = []
                for it in obj.get("content"):
                    t = self._extract_text(it)
                    if t:
                        parts.append(t)
                return "".join(parts)
            # Некоторые форматы кладут текст в data.text или message.content
            for key in ("text", "message", "data"):
                v = obj.get(key)
                t = self._extract_text(v)
                if t:
                    return t
        elif isinstance(obj, list):
            parts = [self._extract_text(it) for it in obj]
            parts = [p for p in parts if p]
            return "\n".join(parts)
        elif isinstance(obj, str):
            return obj
        return ""

    def _is_user_event(self, obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "user":
                return True
            msg = obj.get("message")
            if isinstance(msg, dict) and msg.get("role") == "user":
                return True
        return False

    def _is_assistant_event(self, obj: Any) -> bool:
        if isinstance(obj, dict):
            if obj.get("type") == "assistant":
                return True
            msg = obj.get("message")
            if isinstance(msg, dict) and msg.get("role") == "assistant":
                return True
        return False

    def _box(self, text: str) -> str:
        """Простая рамка для текста пользователя."""
        lines = text.splitlines() or [""]
        width = max(len(l) for l in lines)
        top = "┌" + "─" * (width + 2) + "┐"
        mid = ["│ " + l.ljust(width) + " │" for l in lines]
        bot = "└" + "─" * (width + 2) + "┘"
        return "\n".join([top, *mid, bot])
    
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