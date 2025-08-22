"""
🤖 DonutBuffer Ambient Agent System

Автоматический мониторинг и анализ проекта через cursor-agent.
"""

from .agent_injector import AgentInjector
from .event_system import EventSystem, Event
from .github_monitor import GitHubMonitor  
from .prompt_generator import PromptGenerator
from .event_handlers import EventHandlers
from .ambient_agent import AmbientAgent

__version__ = "1.0.0"
__author__ = "DonutBuffer Ambient Agent"

__all__ = [
    'AgentInjector',
    'EventSystem', 
    'Event',
    'GitHubMonitor',
    'PromptGenerator',
    'EventHandlers',
    'AmbientAgent'
] 