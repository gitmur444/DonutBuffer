"""
🧙‍♂️ DonutBuffer AI Wizard - MCP Setup

Настройка GitHub MCP Server и создание конфигурации.
"""

import json
from pathlib import Path
from ..core.base import BaseWizard

class MCPSetup(BaseWizard):
    """Настройка MCP Server"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        
    def setup_github_mcp(self) -> bool:
        """Шаг 3: Настройка GitHub MCP Server"""
        self.print_step(3, "Настройка GitHub MCP Server")
        
        # Просто создаем MCP конфигурацию - клонирование не нужно
        self.print_success("GitHub MCP интеграция будет настроена через конфигурацию")
        
        # Создаем MCP конфигурацию
        return self.create_mcp_config()
    

    
    def create_mcp_config(self) -> bool:
        """Создание конфигурации MCP"""
        mcp_config_path = self.project_dir / "github_mcp_server" / "config" / "mcp_config.json"
        
        # Создаем папку если не существует
        mcp_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Упрощенная конфигурация - использует стандартный GitHub MCP сервер
        mcp_config = {
            "mcpServers": {
                "github": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-github"],
                    "env": {
                        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}",
                        "GITHUB_HOST": "https://github.com"
                    }
                }
            }
        }
        
        with open(mcp_config_path, 'w') as f:
            json.dump(mcp_config, f, indent=2)
            
        self.print_success(f"MCP конфигурация создана: {mcp_config_path}")
        self.print_success("Использует стандартный GitHub MCP сервер через npx")
        return True 