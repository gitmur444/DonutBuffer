"""
SafeShellTool - Secure shell execution with command whitelist
"""

import subprocess
import warnings
from typing import Dict, Any, List, Union
from rich.console import Console

console = Console()

class SafeShellTool:
    """
    Secure shell tool with command validation.
    
    Simple implementation using subprocess for maximum compatibility.
    
    Features:
    - Command whitelist validation
    - Safe execution checks
    - No complex dependencies
    """
    
    def __init__(self):
        """Initialize with command whitelist"""
        self.allowed_commands = {
            'ls', 'cat', 'grep', 'head', 'tail', 'find', 'wc', 'sort', 'pwd',
            'echo', 'which', 'whoami', 'date', 'uptime', 'df', 'du', 'ps',
            'top', 'free', 'uname', 'hostname', 'id', 'groups', 'env'
        }
        self.name = "safe_shell"
        self.description = "Execute safe shell commands with whitelist validation"
        
    def validate_command(self, command: str) -> bool:
        """Validate command against whitelist"""
        if not command or not command.strip():
            return False
            
        # Handle both string and semicolon-separated commands
        commands = command.split(';') if ';' in command else [command]
        
        for cmd in commands:
            cmd = cmd.strip()
            if not cmd:
                continue
                
            # Extract base command (first word)
            cmd_parts = cmd.split()
            if not cmd_parts:
                continue
                
            base_command = cmd_parts[0]
            
            # Remove common prefixes
            if base_command.startswith('sudo'):
                return False  # Never allow sudo
            
            if base_command not in self.allowed_commands:
                return False
                
        return True
    
    def _run(self, commands: Union[str, List[str]], **kwargs) -> str:
        """
        Execute shell commands safely using subprocess.
        
        Args:
            commands: Command(s) to execute
            **kwargs: Additional arguments (ignored for compatibility)
            
        Returns:
            Command output
            
        Raises:
            ValueError: If command is not in whitelist
        """
        
        # Normalize commands to list format
        if isinstance(commands, str):
            cmd_list = [commands]
        else:
            cmd_list = commands
            
        # Validate each command
        for cmd in cmd_list:
            if not self.validate_command(cmd):
                error_msg = f"❌ Command not in whitelist: '{cmd}'"
                console.print(error_msg, style="red")
                raise ValueError(error_msg)
        
        # All commands validated - execute using subprocess
        console.print(f"🔍 [SafeShellTool] Executing: {cmd_list}", style="dim")
        
        results = []
        for cmd in cmd_list:
            try:
                result = subprocess.run(
                    cmd, 
                    shell=True, 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
                if result.returncode != 0:
                    output = f"Command failed (exit code {result.returncode}):\n{result.stderr}"
                else:
                    output = result.stdout
                results.append(output)
            except subprocess.TimeoutExpired:
                results.append(f"Command timed out: {cmd}")
            except Exception as e:
                results.append(f"Error executing command: {str(e)}")
        
        return "\n".join(results)
    
    def run(self, tool_input: Union[str, Dict[str, Any]]) -> str:
        """
        Override run method to handle both dict and string inputs safely.
        
        Args:
            tool_input: Either a string command or dict with 'commands' key
            
        Returns:
            Command output
        """
        
        # Handle different input formats
        if isinstance(tool_input, str):
            commands = tool_input
        elif isinstance(tool_input, dict):
            commands = tool_input.get('commands', tool_input.get('command', ''))
        else:
            raise ValueError(f"Invalid input type: {type(tool_input)}")
            
        # Use our safe _run method
        return self._run(commands)
    
    def execute(self, params: Dict[str, Any]) -> str:
        """
        Execute method for compatibility with our existing node system.
        
        Args:
            params: Dict containing 'command' key
            
        Returns:
            Command output
        """
        command = params.get('command', '')
        return self.run(command)
    
    def add_allowed_command(self, command: str) -> None:
        """Add a command to the whitelist"""
        self.allowed_commands.add(command)
        console.print(f"✅ Added '{command}' to whitelist", style="green")
    
    def remove_allowed_command(self, command: str) -> None:
        """Remove a command from the whitelist"""
        if command in self.allowed_commands:
            self.allowed_commands.remove(command)
            console.print(f"❌ Removed '{command}' from whitelist", style="yellow")
    
    def get_allowed_commands(self) -> set:
        """Get current whitelist"""
        return self.allowed_commands.copy()
    
    def __repr__(self) -> str:
        return f"SafeShellTool(allowed_commands={len(self.allowed_commands)})" 