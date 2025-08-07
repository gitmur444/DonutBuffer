"""ChatTool for conversational AI interaction with user questions"""

import os
from typing import Dict, Any, List, Optional
from .openai_config import OpenAIConfig

class ChatTool:
    """Universal tool for conversational AI that can answer general questions using LLM"""
    
    def __init__(self, user_task: str, conversation_history: List[str] = None):
        self.name = "chat"
        self.description = "Universal conversational AI tool for answering questions and engaging with users"
        self.user_task = user_task
        self.conversation_history = conversation_history or []
    
    def execute(self, params: Dict[str, Any]) -> str:
        """Execute chat interaction with user question
        
        Args:
            params: Dictionary with optional 'question', 'context', 'style' parameters
        """
        try:
            question = params.get('question', self.user_task)
            additional_context = params.get('context', '')
            response_style = params.get('style', 'friendly')
            
            return self.generate_response(question, additional_context, response_style)
            
        except Exception as e:
            return f"❌ Chat error: {str(e)}"
    
    def generate_response(self, question: str, additional_context: str = "", response_style: str = "friendly") -> str:
        """Generate conversational response using OpenAI
        
        Args:
            question: User's question to answer
            additional_context: Any additional context to consider
            response_style: Style of response (friendly, professional, technical, etc.)
        """
        try:
            # Create conversation history context
            history_context = ""
            if self.conversation_history:
                history_context = f"\nRecent conversation history:\n" + "\n".join(self.conversation_history[-5:])
            
            # Detect language and create appropriate system prompt
            system_prompt = f"""You are a helpful AI assistant that provides conversational responses to user questions.

            Guidelines:
            - Response style: {response_style}
            - Be conversational and natural
            - Detect the user's language and respond in the same language
            - For simple questions, provide direct, helpful answers
            - If you don't have specific information, say so honestly
            - Keep responses concise but informative
            - Be context-aware and refer to previous interactions when relevant
            
            Context about current environment:
            - This is an AI Test Planner system for DonutBuffer C++ project
            - You can help with general questions, explanations, and conversation
            - You have access to conversation history and additional context when provided
            
            Special handling for common question types:
            - "что я только что спросил?" / "what did I just ask?" → refer to the immediate previous question
            - Questions about location/directory → you're in DonutBuffer testing environment
            - Questions about capabilities → explain what you can help with
            - Questions about memory → acknowledge you can remember conversation context
            """
            
            user_prompt = f"""User question: "{question}"
            
            {additional_context}
            {history_context}
            
            Please provide a helpful, conversational response that directly addresses the user's question. 
            Match their language and tone - if they're casual, be casual; if formal, be formal.
            
            CRITICAL: Always respond in the same language as the user's question."""

            response = OpenAIConfig.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                use_case="conversation"
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"❌ Failed to generate response: {str(e)}"
    
    def add_to_history(self, interaction: str):
        """Add interaction to simple conversation history"""
        self.conversation_history.append(interaction)
        
        # Keep only last 5 interactions to avoid context bloat
        if len(self.conversation_history) > 5:
            self.conversation_history = self.conversation_history[-5:]
    
    def run(self, **kwargs) -> str:
        """Standard run interface"""
        return self.execute(kwargs) 