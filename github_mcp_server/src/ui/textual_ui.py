"""
Rich + Textual UI that exactly mimics cursor-agent design
"""

import asyncio
import json
import subprocess
import threading
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Input, Static
from textual import events
import os


class CursorAgentUI(App):
    """Textual app that mimics cursor-agent exactly"""
    
    CSS = """
    Screen {
        background: #1a1a1a;
    }
    
    #header {
        height: 3;
        background: #1a1a1a;
        color: white;
        border: round white;
    }
    
    #main_output {
        height: 1fr;
        background: #1a1a1a;
        color: white;
        border: round white;
        margin: 1 0;
    }
    
    #input_area {
        height: 3;
        background: #1a1a1a;
        color: white;
        border: round white;
    }
    
    #footer {
        height: 1;
        background: #1a1a1a;
        color: #888888;
    }
    
    Input {
        background: #1a1a1a;
        color: white;
        border: none;
    }
    
    Static {
        background: #1a1a1a;
        color: white;
    }
    """

    output_content = reactive("", layout=True)
    
    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        with Container():
            # Header like cursor-agent
            yield Static(self._get_header_text(), id="header")
            
            # Main output area
            yield Static("", id="main_output")
            
            # Input area with arrow and placeholder
            with Container(id="input_area"):
                yield Input(placeholder="→ Add a follow-up", id="user_input")
            
            # Footer with model info
            yield Static("  Claude 4 Sonnet · 0%", id="footer")

    def _get_header_text(self) -> str:
        """Get header text like cursor-agent"""
        cwd = os.getcwd()
        project_name = os.path.basename(cwd)
        return f"  Cursor Agent\n  ~/{project_name} · main"

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission"""
        if event.value.strip():
            # Add user message to output
            await self._add_user_message(event.value)
            
            # Clear input
            self.query_one("#user_input", Input).value = ""
            
            # Stream agent response
            await self._stream_agent_response(event.value)

    async def _add_user_message(self, message: str) -> None:
        """Add user message in a box to output"""
        current_output = self.query_one("#main_output", Static)
        
        # Create box for user message (like cursor-agent)
        width = 100  # Approximate terminal width
        box_content = f"┌{'─' * (width - 2)}┐\n"
        box_content += f"│ {message:<{width - 4}} │\n"
        box_content += f"└{'─' * (width - 2)}┘\n\n"
        
        current_output.update(current_output.renderable + box_content)

    async def _stream_agent_response(self, prompt: str) -> None:
        """Stream response from cursor-agent"""
        current_output = self.query_one("#main_output", Static)
        
        # Add "Assistant:" header
        current_output.update(current_output.renderable + "Assistant:\n")
        
        # Run cursor-agent in subprocess
        cmd = ["cursor-agent", prompt, "--print", "--output-format", "stream-json"]
        
        def run_agent():
            try:
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    bufsize=1
                )
                
                for line in iter(process.stdout.readline, ''):
                    try:
                        json_event = json.loads(line.strip())
                        if json_event.get("type") == "assistant" and "message" in json_event:
                            content_parts = json_event["message"]["content"]
                            for part in content_parts:
                                if part.get("type") == "text":
                                    text = part["text"]
                                    # Update UI in main thread
                                    self.call_from_thread(self._append_text, text)
                        elif json_event.get("type") == "result":
                            self.call_from_thread(self._append_text, "\n\n")
                            break
                    except json.JSONDecodeError:
                        continue
                        
                process.wait()
                
            except Exception as e:
                self.call_from_thread(self._append_text, f"Error: {e}\n")
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()

    def _append_text(self, text: str) -> None:
        """Append text to output (called from thread)"""
        current_output = self.query_one("#main_output", Static)
        current_output.update(current_output.renderable + text)
        
        # Scroll to bottom
        current_output.scroll_end()

    async def on_key(self, event: events.Key) -> None:
        """Handle keyboard events"""
        if event.key == "ctrl+c":
            self.exit()


def run_textual_ui():
    """Launch the Textual UI"""
    app = CursorAgentUI()
    app.run()


if __name__ == "__main__":
    run_textual_ui()
