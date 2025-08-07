"""
Memory setup for AI Test Planner
"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from rich.console import Console

console = Console()

def setup_simple_memory():
    """Setup simple in-memory chat history"""
    # Just use simple in-memory storage for chat history
    checkpointer = InMemorySaver()
    store = InMemoryStore()
    console.print("[green]✅ Simple memory enabled[/green]")
    
    return checkpointer, store 