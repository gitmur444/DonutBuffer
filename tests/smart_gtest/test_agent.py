#!/usr/bin/env python3
"""
Smart GTest Agent - Simple AI assistant using LangGraph
"""

import os
import asyncio
from typing import TypedDict
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

class AgentState(TypedDict):
    """Simple state for the agent"""
    user_input: str
    response: str

class SmartGTestAgent:
    """Simple AI Agent for testing assistance"""
    
    def __init__(self):
        """Initialize the agent"""
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            temperature=0.1
        )
        self.graph = self._create_graph()
        
    def _create_graph(self) -> StateGraph:
        """Create simple LangGraph workflow"""
        workflow = StateGraph(AgentState)
        workflow.add_node("generate_response", self._generate_response)
        workflow.set_entry_point("generate_response")
        workflow.add_edge("generate_response", END)
        return workflow.compile()
    
    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate response using LLM"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Smart GTest Agent, an AI assistant for C++ testing and ring buffer analysis.
             Help with DonutBuffer performance testing, mutex vs lockfree implementations, and GTest framework usage.
             Provide clear, actionable technical advice."""),
            ("human", "{user_input}")
        ])
        
        response = await self.llm.ainvoke(
            prompt.format_messages(user_input=state["user_input"])
        )
        
        state["response"] = response.content
        return state
    
    async def chat(self, user_input: str) -> str:
        """Process user message and return response"""
        result = await self.graph.ainvoke({"user_input": user_input, "response": ""})
        return result["response"]

async def main():
    """Single interaction with the agent"""
    print("🤖 Smart GTest Agent")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found")
        return
    
    try:
        user_input = input("👤 Your question: ").strip()
        
        if not user_input:
            print("❌ No input provided")
            return
            
        agent = SmartGTestAgent()
        response = await agent.chat(user_input)
        print(f"\n🤖 Agent: {response}")
        
    except KeyboardInterrupt:
        print("\n👋 Cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 