"""
Task execution module for AI Test Planner
"""

import json
import sys
from sqlalchemy import create_engine, text
from rich.console import Console
from rich.panel import Panel

from .graph_state import GraphState
from .planner import ask_planner
from .memory_setup import setup_simple_memory
from .graph_builder import build_graph

console = Console()

def run(task: str, thread_id: str = None, user_id: str = "default_user") -> None:
    """Main execution function with simple memory"""
    
    # Setup database connection (only for TestDB nodes)
    db_url = "postgresql://postgres:postgres@localhost:5432/smart_tests"
    engine = None
    
    try:
        engine = create_engine(db_url, echo=False)
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        console.print("[green]✅ Connected to PostgreSQL database[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠️ PostgreSQL not available: {str(e)}[/yellow]")
        console.print("[yellow]💡 Running without database support (shell commands still work)[/yellow]")
        engine = None
    
    # Setup simple memory
    checkpointer, store = setup_simple_memory()
    
    # Simple single session setup
    console.print(f"[blue]🧵 Using session: {thread_id}[/blue]")
    
    # Configuration with thread and user IDs
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": user_id
        }
    }
    
    console.print(f"[blue]🧵 Thread: {thread_id} | 👤 User: {user_id}[/blue]")
    
    max_attempts = 2
    error_msg = ""
    
    for attempt in range(max_attempts):
        try:
            console.print(f"[blue]Plan v{attempt + 1}:[/blue]")
            
            # Generate plan
            plan = ask_planner(task, error_msg)
            console.print(Panel(json.dumps(plan, indent=2, ensure_ascii=False), title="Generated Plan"))
            
            # Build and execute graph
            graph = build_graph(plan, engine, task, checkpointer, store)
            
            # Initialize state - results will accumulate due to LangGraph design
            initial_state: GraphState = {
                "task": task,
                "results": [],
                "current_step": "start"
            }
            
            result = graph.invoke(initial_state, config)
            
            console.print("[green]✅ Execution completed successfully[/green]")
            
            # Display simple result
            if result.get("results"):
                latest_result = result["results"][-1]  # Show the current result
                console.print(Panel(str(latest_result), title="Result"))
            else:
                console.print(Panel("No results generated", title="Results"))
            
            # Simple completion message
            console.print(f"[dim]✨ Session: {thread_id}[/dim]")
            
            return
            
        except Exception as e:
            error_msg = str(e)
            console.print(f"[red]❌ Attempt {attempt + 1} failed: {error_msg}[/red]")
            
            if attempt == max_attempts - 1:
                console.print("[red]Failed after 2 attempts[/red]")
                sys.exit(1) 