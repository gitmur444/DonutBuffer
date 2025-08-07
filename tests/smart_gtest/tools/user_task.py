"""UserTask tool for providing user's original request as context"""

from typing import Dict, Any

class UserTaskTool:
    """Tool that provides the original user's task/prompt"""
    
    def __init__(self, user_task: str):
        self.user_task = user_task
        self.name = "user_task"
        self.description = "Provides the original user's task/prompt as context"
    
    def execute(self, params: Dict[str, Any]) -> str:
        """Execute - return the original user's task"""
        return f"User's original request: {self.user_task}"
    
    def run(self, **kwargs) -> str:
        """Return the original user's task"""
        return f"User's original request: {self.user_task}"


 