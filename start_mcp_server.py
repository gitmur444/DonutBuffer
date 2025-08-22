#!/usr/bin/env python3
"""Start GitHub MCP Server for DonutBuffer"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN не установлен")
        print("Экспортируйте токен: export GITHUB_TOKEN='your_token_here'")
        sys.exit(1)
    
    mcp_server_path = Path("../github-mcp-server/github-mcp-server")
    if not mcp_server_path.exists():
        print(f"❌ MCP Server не найден: {mcp_server_path}")
        print("Запустите сначала: python setup_github_integration.py")
        sys.exit(1)
    
    print("🚀 Запуск GitHub MCP Server для DonutBuffer...")
    
    env = os.environ.copy()
    env.update({
        "GITHUB_PERSONAL_ACCESS_TOKEN": github_token,
        "GITHUB_HOST": "https://github.com",
        "GITHUB_TOOLSETS": "actions,pull_requests,repos,issues"
    })
    
    try:
        subprocess.run([str(mcp_server_path), "stdio"], env=env)
    except KeyboardInterrupt:
        print("\n🛑 MCP Server остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска MCP Server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
