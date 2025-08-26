"""
Interactive CLI using prompt_toolkit - professional solution
"""

import threading
import time
import os
import sys
import subprocess
import json
import signal
from pathlib import Path
import select

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style

from rich.console import Console
from rich.panel import Panel

# Add parent directory to sys.path for absolute imports
sys.path.append(str(Path(__file__).parent.parent))
from ..core.base_wizard import Colors

console = Console()
stop_event = threading.Event()

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    stop_event.set()
    console.print(f"\n[yellow]Выход...[/yellow]")
    sys.exit(0)

def draw_header():
    """Draw header like cursor-agent"""
    header_panel = Panel(
        f"  Cursor Agent\n  ~/{os.path.basename(os.getcwd())} · main",
        border_style="white",
        padding=(0, 1),
        width=console.size.width
    )
    console.print(header_panel)

# Define style for prompt_toolkit
style = Style.from_dict({
    'input': '#ffffff',
    'placeholder': '#888888 italic',
})

def get_user_input():
    """Get input using prompt_toolkit with cursor-agent style"""
    try:
        # Сбрасываем возможные оставшиеся escape/ASCII последовательности из stdin
        try:
            while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                try:
                    # Читаем и отбрасываем мусор
                    _ = sys.stdin.read(1024)
                except Exception:
                    break
        except Exception:
            pass
        user_input = prompt(
            '→ ',
            placeholder='Add a follow-up',
            style=style,
            mouse_support=False,
            complete_style='column',
            wrap_lines=True,
        )
        return user_input.strip()
    except (EOFError, KeyboardInterrupt):
        stop_event.set()
        return None

def display_user_message(message):
    """Display user message in a box like cursor-agent"""
    user_panel = Panel(
        message,
        border_style="green",
        padding=(0, 1),
        width=console.size.width
    )
    console.print(user_panel)

def stream_agent_response(prompt_text):
    """Stream agent response using cursor-agent --print --output-format stream-json"""
    cmd = ["cursor-agent", prompt_text, "--print", "--output-format", "stream-json"]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        
        console.print(f"\n[blue]Assistant:[/blue]")
        
        for line in iter(process.stdout.readline, ''):
            if stop_event.is_set():
                process.terminate()
                break
                
            try:
                json_event = json.loads(line.strip())
                if json_event.get("type") == "assistant" and "message" in json_event:
                    content_parts = json_event["message"]["content"]
                    for part in content_parts:
                        if part.get("type") == "text":
                            text = part["text"]
                            console.print(text, end="")
                elif json_event.get("type") == "result":
                    console.print()  # Final newline
                    break
            except json.JSONDecodeError:
                # Skip malformed JSON lines
                continue
            except Exception as e:
                console.print(f"\n[red]Error processing response: {e}[/red]")
                
        process.stdout.close()
        process.stderr.close()
        process.wait()
        
    except Exception as e:
        console.print(f"[red]Error running cursor-agent: {e}[/red]")

def run_interactive():
    """Main interactive loop with prompt_toolkit"""
    # Если stdout не TTY (например, запуск через пайп), не запускаем TUI
    if not sys.stdout.isatty():
        console.print("[yellow]TUI отключен (не TTY). Запустите ./wizard напрямую в терминале.[/yellow]")
        return
    # Set up signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Draw header like cursor-agent
    draw_header()
    
    # Footer info like cursor-agent
    console.print("\n  [dim]Claude 4 Sonnet · 0%[/dim]")
    
    while not stop_event.is_set():
        console.print()  # Spacing
        
        user_input = get_user_input()
        if user_input is None or stop_event.is_set():
            break
            
        if user_input:
            display_user_message(user_input)
            stream_agent_response(user_input)
            console.print()  # Extra spacing for next iteration