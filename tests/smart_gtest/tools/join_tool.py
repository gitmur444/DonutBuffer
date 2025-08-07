"""JoinTool for combining results from multiple inputs"""

from typing import Dict, Any

class JoinTool:
    """Tool that combines results from multiple inputs"""
    
    def __init__(self):
        self.name = "join"
        self.description = "Combines results from multiple inputs with configurable mode"
    
    def execute(self, params: Dict[str, Any]) -> str:
        """Execute join operation - this will be called specially by join node"""
        mode = params.get('mode', 'all')
        separator = params.get('separator', '\n---\n')
        
        # Это специальный узел - он получит доступ к state.results через особую node функцию
        # Возвращаем параметры для обработки в специальной join node функции
        return f"JOIN_PARAMS:{mode}|{separator}"
    
    def run(self, **kwargs) -> str:
        """Standard run interface"""
        return self.execute(kwargs) 