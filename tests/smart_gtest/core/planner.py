"""
AI Planning module using GPT-4o for generating LangGraph workflows
"""

import json
import re
from typing import Dict, Any

from tools.openai_config import OpenAIConfig
from .examples import get_examples_text

def ask_planner(task: str, error_msg: str = "") -> Dict[str, Any]:
    """Ask GPT-4o to generate execution plan"""
    
    # Load examples from external module
    examples_text = get_examples_text()
    
    system_prompt = f"""
        You are an AI-Driven Test Assistant which associates itself with the DonutBuffer 
        project testing system. Your task is to generate a LangGraph graph to solve the user's problem. 

        You have the following nodes available:
        1. UserTask - Provides the original user's task/prompt as context
        params: {{}} (automatically contains the user's request)

        2. Chat - Universal conversational AI for answering questions and general interaction
        params: {{"question": "optional override", "context": "additional context", "style": "friendly|professional|technical"}}
        - Use this for: simple questions, explanations, conversations, "what did I just ask?" type queries
        - Automatically detects language and responds appropriately
        - Can reference conversation history and context

        3. TestDB - Execute database queries using natural language intent (Smart SQL)
        params: {{"intent": "describe what you want to query", "context": "optional additional context"}}
        - Use natural language to describe what data you need
        - Smart SQL automatically generates appropriate queries based on database schema
        - Examples: "show all tests", "find failed tests", "get test statistics"
        
        4. Shell - Execute safe shell commands (ls, cat, grep, head, tail, find)
        params: {{"command": "ls -la logs/"}}

        5. Join - Join results from multiple inputs  
        params: {{"mode": "all" | "any", "separator": "\\n---\\n"}}
        - "all": Wait for ALL incoming results (default)
        - "any": Execute when ANY result arrives
        - "separator": How to Join multiple results

        6. LLMFormat - Convert raw data into human-readable responses using AI
        params: {{"prompt": "template", "format": "summary|report|list|paragraph"}}
        - "prompt": Custom instruction for formatting (default: "Convert this data to a friendly human summary")
        - "format": Output structure (default: "summary")

        {examples_text}

        Return ONLY valid JSON, no explanations.
    """

    user_msg = f"Task: {task}"
    if error_msg:
        user_msg += f"\nPrevious error: {error_msg}\nGenerate a corrected plan."

    try:
        # Use centralized OpenAI config
        response = OpenAIConfig.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            use_case="planning"
        )
        
        plan_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
        if json_match:
            plan_text = json_match.group(0)
            
        plan = json.loads(plan_text)
        
        # Validate plan structure
        if 'nodes' not in plan or 'edges' not in plan:
            raise ValueError("Plan missing nodes or edges")
        
        # Basic plan structure is valid
        
        return plan
        
    except Exception as e:
        raise RuntimeError(f"Failed to generate plan: {str(e)}") 