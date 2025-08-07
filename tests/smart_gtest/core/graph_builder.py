"""
LangGraph building functions for AI Test Planner
"""

from typing import Dict, Any
from collections import Counter
from langgraph.graph import StateGraph, END

from .graph_state import GraphState
from .tools_setup import create_tools, create_tool_mapping, calculate_node_degrees
from tools import LLMFormatTool

def create_join_node_function(params: Dict[str, Any]):
    """Create a node function for Join operations"""
    def join_node_fn(state: GraphState) -> Dict[str, Any]:
        try:
            mode = params.get('mode', 'all')
            separator = params.get('separator', '\n---\n')
            
            # Access accumulated results from state
            accumulated_results = state.get('results', [])
            
            if not accumulated_results:
                return {"results": ["No results to join"]}
            
            if mode == 'any':
                # For 'any' take first available result  
                result = accumulated_results[0] if accumulated_results else "No results available"
            else:
                # mode == 'all' (default) - combine all results
                result = separator.join(str(r) for r in accumulated_results)
            
            return {"results": [f"JOINED: {result}"]}
        except Exception as e:
            return {"results": [f"Join Error: {str(e)}"]}
    
    return join_node_fn

def create_llm_format_node_function(tool: Any, params: Dict[str, Any]):
    """Create a node function for LLM formatting operations"""
    def format_node_fn(state: GraphState) -> Dict[str, Any]:
        try:
            prompt_template = params.get('prompt', LLMFormatTool.DEFAULT_PROMPT)
            format_style = params.get('format', LLMFormatTool.DEFAULT_FORMAT)
            
            # Access accumulated results and user context from state
            accumulated_results = state.get('results', [])
            user_task = state.get('task', '')  # Get original user request
            
            if not accumulated_results:
                return {"results": ["No data to format"]}
            
            # Use LLMFormatTool to convert raw data to human-readable format with context
            formatted_result = tool.format_data(
                accumulated_results, 
                prompt_template, 
                format_style,
                user_context=user_task  # Pass user's original request
            )
            
            return {"results": [formatted_result]}
        except Exception as e:
            return {"results": [f"LLM Format Error: {str(e)}"]}
    
    return format_node_fn

def create_chat_node_function(tool: Any, params: Dict[str, Any]):
    """Create a node function for Chat operations"""
    def chat_node_fn(state: GraphState) -> Dict[str, Any]:
        try:
            # Get user's original task from state
            user_task = state.get('task', '')
            
            # Use question from params or fall back to user task
            question = params.get('question', user_task)
            additional_context = params.get('context', '')
            response_style = params.get('style', 'friendly')
            
            # Generate response using ChatTool
            result = tool.generate_response(question, additional_context, response_style)
            
            # Add simple history tracking
            tool.add_to_history(f"Q: {question}")
            tool.add_to_history(f"A: {result[:50]}...")
            
            return {"results": [result]}
        except Exception as e:
            return {"results": [f"Chat Error: {str(e)}"]}
    
    return chat_node_fn

def create_regular_node_function(tool: Any, params: Dict[str, Any]):
    """Create a node function for regular tool operations"""
    def node_fn(state: GraphState) -> Dict[str, Any]:
        try:
            result = tool.execute(params)
            return {"results": [result]}
        except Exception as e:
            return {"results": [f"Error: {str(e)}"]}
    
    return node_fn

def build_graph_nodes(graph: StateGraph, plan: Dict[str, Any], tools: Dict):
    """Add all nodes to the graph with proper tool assignment"""
    tool_mapping = create_tool_mapping(tools)
    
    for node_spec in plan['nodes']:
        node_id = node_spec['id']
        node_type = node_spec['type']
        params = node_spec['params']
        
        # Validate node type
        if node_type not in tool_mapping:
            raise ValueError(f"Unknown node type: {node_type}")
        
        # Create appropriate node function
        if node_type == 'Join':
            node_fn = create_join_node_function(params)
        elif node_type == 'LLMFormat':
            tool = tool_mapping[node_type]
            node_fn = create_llm_format_node_function(tool, params)
        elif node_type == 'Chat':
            tool = tool_mapping[node_type]
            node_fn = create_chat_node_function(tool, params)
        else:
            tool = tool_mapping[node_type]
            node_fn = create_regular_node_function(tool, params)
        
        # Add node to graph
        graph.add_node(node_id, node_fn)

def setup_graph_flow(graph: StateGraph, plan: Dict[str, Any], in_degree: Counter):
    """Configure graph entry and exit points"""
    # Add edges
    for edge in plan['edges']:
        graph.add_edge(edge['source'], edge['target'])

    # Set entry point (nodes with no incoming edges)
    entry_nodes = [node['id'] for node in plan['nodes'] if in_degree[node['id']] == 0]
    
    if entry_nodes:
        # Set ALL nodes with no incoming edges as entry points
        for entry_node in entry_nodes:
            graph.set_entry_point(entry_node)
        
        # Set finish point (nodes with no outgoing edges)
        outgoing_nodes = {edge['source'] for edge in plan['edges']}
        all_nodes = {node['id'] for node in plan['nodes']}
        terminal_nodes = all_nodes - outgoing_nodes
        
        for terminal_node in terminal_nodes:
            graph.add_edge(terminal_node, END)
    else:
        # Fallback: use first node if no edges
        if plan['nodes']:
            entry_node = plan['nodes'][0]['id']
            graph.set_entry_point(entry_node)
            graph.add_edge(entry_node, END)

def build_graph(plan: Dict[str, Any], db_engine, user_task: str, checkpointer, store) -> StateGraph:
    """Build LangGraph from plan - simple version"""
    
    # Create tools
    tools = create_tools(db_engine, user_task)
    
    # Calculate graph structure
    in_degree = calculate_node_degrees(plan)
    
    # Build graph
    graph = StateGraph(GraphState)
    
    # Add nodes
    build_graph_nodes(graph, plan, tools)
    
    # Configure entry/exit points
    setup_graph_flow(graph, plan, in_degree)

    # Compile with simple memory
    return graph.compile(checkpointer=checkpointer, store=store) 