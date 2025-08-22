"""
🧙‍♂️ DonutBuffer AI Wizard Package

Модульная система настройки AI-анализа для DonutBuffer проекта.
"""

from .wizard import DonutAIWizard
from .core import Colors, BaseWizard
from .env_manager import EnvManager
from .dependencies import DependencyChecker
from .github_setup import GitHubSetup  
from .mcp_setup import MCPSetup
from .integration_test import IntegrationTest

__version__ = "1.0.0"
__author__ = "DonutBuffer AI Wizard"

__all__ = [
    'DonutAIWizard',
    'Colors', 
    'BaseWizard',
    'EnvManager',
    'DependencyChecker',
    'GitHubSetup',
    'MCPSetup', 
    'IntegrationTest'
] 