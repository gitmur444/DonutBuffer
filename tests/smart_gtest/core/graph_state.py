"""
Graph state and data structures for AI Test Planner
"""

from typing import Dict, List, Any, Annotated
from dataclasses import dataclass
from operator import add
from typing import TypedDict

class GraphState(TypedDict):
    """State for the LangGraph workflow"""
    task: str
    results: Annotated[List[str], add]
    current_step: str

@dataclass
class PlanNode:
    id: str
    type: str
    params: Dict[str, Any]

@dataclass
class PlanEdge:
    source: str
    target: str 