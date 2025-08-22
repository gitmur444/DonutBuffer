#!/usr/bin/env python3
"""DonutBuffer CI/CD Monitoring with Cursor Agent"""

import subprocess
import sys
import os
from datetime import datetime

def run_cursor_query(query):
    """Run Cursor Agent query with error handling."""
    try:
        result = subprocess.run(
            ["cursor-agent", "--print", "--output-format", "text", query],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Timeout"
    except Exception as e:
        return f"Error: {e}"

def main():
    repo = "DonutBuffer"  # Измените на ваш полный путь репозитория
    
    print("🚀 Мониторинг CI/CD для DonutBuffer")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check failed workflows
    print("\n🔍 Упавшие workflow за последние 24 часа:")
    print("-" * 40)
    failed_query = f"Найди все failed GitHub Actions workflow runs за последние 24 часа в репозитории {repo} и дай краткий анализ причин"
    print(run_cursor_query(failed_query))
    
    # Check PR status
    print("\n🔍 Статус Pull Requests:")
    print("-" * 40)
    pr_query = f"Покажи все open pull requests в {repo} с их статусом проверок и возможными проблемами"
    print(run_cursor_query(pr_query))
    
    # Performance analysis
    print("\n🔍 Производительность тестов:")
    print("-" * 40)
    perf_query = f"Проанализируй время выполнения тестов в последних GitHub Actions для {repo} и предложи оптимизации"
    print(run_cursor_query(perf_query))
    
    print("\n✅ Анализ завершен!")

if __name__ == "__main__":
    main()
