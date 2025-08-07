"""
Tools setup and configuration for AI Test Planner
"""

from typing import Dict, Any
from collections import Counter
from langchain_community.utilities import SQLDatabase

from tools import SafeSQLTool, SafeShellTool, UserTaskTool, JoinTool, LLMFormatTool, ChatTool

def create_tools(db_engine, user_task: str):
    """Create tool instances for graph execution"""
    tools = {
        'shell': SafeShellTool(),
        'user_task': UserTaskTool(user_task),
        'join': JoinTool(),
        'llm_format': LLMFormatTool(),
        'chat': ChatTool(user_task)
    }
    
    # Add SQL tool only if database is available
    if db_engine:
        db = SQLDatabase(db_engine)
        tools['sql'] = SafeSQLTool(db)
    
    return tools

def create_tool_mapping(tools: Dict) -> Dict[str, Any]:
    """Create mapping from node types to tools"""
    tool_mapping = {
        'UserTask': tools['user_task'],
        'Chat': tools['chat'],
        'Shell': tools['shell'],
        'Join': tools['join'],
        'LLMFormat': tools['llm_format']
    }
    
    # Add TestDB only if SQL tool is available
    if 'sql' in tools:
        tool_mapping['TestDB'] = tools['sql']
    
    return tool_mapping

def calculate_node_degrees(plan: Dict[str, Any]) -> Counter:
    """Calculate incoming edge count for each node"""
    in_degree = Counter()
    for edge in plan['edges']:
        in_degree[edge['target']] += 1
    return in_degree 