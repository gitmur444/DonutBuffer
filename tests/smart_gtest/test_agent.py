#!/usr/bin/env python3
"""
Smart GTest Agent - AI-powered testing assistant using LangGraph
Integrates with the DonutBuffer testing system to provide intelligent test analysis and recommendations.
"""

import os
import asyncio
from typing import TypedDict, List, Dict, Any
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolInvocation
import json

# Load environment variables
load_dotenv()

class AgentState(TypedDict):
    """State for the Smart GTest Agent"""
    messages: List[Dict[str, Any]]
    current_task: str
    test_context: Dict[str, Any]
    user_input: str
    response: str

class SmartGTestAgent:
    """AI Agent for Smart GTest system integration"""
    
    def __init__(self):
        """Initialize the agent with LLM and graph"""
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            temperature=0.1
        )
        self.graph = self._create_graph()
        
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_input", self._analyze_input)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("format_output", self._format_output)
        
        # Add edges
        workflow.set_entry_point("analyze_input")
        workflow.add_edge("analyze_input", "generate_response")
        workflow.add_edge("generate_response", "format_output")
        workflow.add_edge("format_output", END)
        
        return workflow.compile()
    
    async def _analyze_input(self, state: AgentState) -> AgentState:
        """Analyze user input and determine context"""
        user_input = state["user_input"]
        
        # Simple analysis - could be more sophisticated
        test_keywords = ["test", "performance", "benchmark", "ring buffer", "mutex", "lockfree"]
        is_test_related = any(keyword in user_input.lower() for keyword in test_keywords)
        
        state["test_context"] = {
            "is_test_related": is_test_related,
            "detected_keywords": [kw for kw in test_keywords if kw in user_input.lower()],
            "needs_technical_analysis": is_test_related
        }
        
        return state
    
    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate response using LLM"""
        user_input = state["user_input"]
        test_context = state["test_context"]
        
        # Create system prompt based on context
        if test_context["is_test_related"]:
            system_prompt = """You are a Smart GTest Agent, an AI assistant specialized in C++ testing, 
            particularly for ring buffer performance analysis. You help developers understand test results, 
            suggest optimizations, and analyze performance benchmarks for mutex vs lockfree implementations.
            
            You have expertise in:
            - C++ ring buffer implementations
            - Performance testing and benchmarking
            - Mutex vs lockfree concurrency patterns
            - GTest framework usage
            - Memory safety and RAII principles
            
            Provide helpful, technical responses that are actionable and specific to the DonutBuffer project."""
        else:
            system_prompt = """You are a helpful AI assistant. Provide clear, concise, and helpful responses 
            to user questions. If the question relates to testing or C++ development, offer relevant technical insights."""
        
        # Generate response
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{user_input}")
        ])
        
        response = await self.llm.ainvoke(
            prompt.format_messages(user_input=user_input)
        )
        
        state["response"] = response.content
        return state
    
    async def _format_output(self, state: AgentState) -> AgentState:
        """Format the final output"""
        # Add any special formatting or test integration here
        response = state["response"]
        test_context = state["test_context"]
        
        if test_context["is_test_related"]:
            # Add test-specific formatting
            formatted_response = f"🧪 **Smart GTest Analysis**\n\n{response}"
            if test_context["detected_keywords"]:
                formatted_response += f"\n\n*Detected keywords: {', '.join(test_context['detected_keywords'])}*"
        else:
            formatted_response = response
            
        state["response"] = formatted_response
        return state
    
    async def process_message(self, user_input: str) -> str:
        """Process a user message and return AI response"""
        initial_state = AgentState(
            messages=[],
            current_task="chat",
            test_context={},
            user_input=user_input,
            response=""
        )
        
        final_state = await self.graph.ainvoke(initial_state)
        return final_state["response"]

async def main():
    """Main interactive loop"""
    print("🤖 Smart GTest Agent - DonutBuffer Testing Assistant")
    print("=" * 50)
    print("Type 'quit', 'exit' or 'bye' to end the conversation")
    print("Ask me about C++ testing, ring buffers, or performance analysis!")
    print()
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key or create a .env file with OPENAI_API_KEY=your_key")
        return
    
    agent = SmartGTestAgent()
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Check for exit conditions
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\n👋 Goodbye! Happy testing!")
                break
                
            if not user_input:
                continue
                
            # Process message
            print("\n🤔 Thinking...")
            response = await agent.process_message(user_input)
            
            # Display response
            print(f"\n🤖 Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Happy testing!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    asyncio.run(main()) 