#!/usr/bin/env python3
"""
AI-Driven Test Planner for DonutBuffer Smart GTest System
Generates LangGraph workflows using GPT-4o for C++ test automation tasks
"""

import sys
import os
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

# Import our core modules
from core import run

console = Console()

# Load environment variables from .env file
script_dir = os.path.dirname(os.path.abspath(__file__))
env_file = os.path.join(script_dir, '.env')
load_dotenv(env_file)

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        console.print("Usage: python ai_test_planner.py 'task description'")
        console.print("Examples:")
        console.print("  python ai_test_planner.py 'Show me test results'")
        console.print("  python ai_test_planner.py 'привет'")
        console.print("  python ai_test_planner.py 'что я только что спросил?'")
        sys.exit(1)
        
    task = sys.argv[1]
    # Simple single session - no complex thread management
    thread_id = "default_session"
    user_id = "default_user"
    
    # Check OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        console.print("[red]OPENAI_API_KEY environment variable required[/red]")
        sys.exit(1)
    
    console.print(Panel(f"Task: {task}", title="AI Test Planner"))
    run(task, thread_id, user_id)

if __name__ == "__main__":
    main() 