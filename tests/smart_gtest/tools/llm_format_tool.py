"""LLMFormatTool for converting raw data into human-readable responses"""

import os
from typing import Dict, Any, List
from .openai_config import OpenAIConfig

class LLMFormatTool:
    """Tool that uses LLM to convert raw data into human-readable format"""
    
    # Default values - defined once here to avoid duplication
    DEFAULT_PROMPT = "Convert this data to a friendly human summary"
    DEFAULT_FORMAT = "summary"
    
    def __init__(self):
        self.name = "llm_format"
        self.description = "Converts raw data into natural language using GPT"
    
    def execute(self, params: Dict[str, Any]) -> str:
        """Execute method for compatibility - should not be used directly for LLMFormat nodes"""
        # This method exists for compatibility but LLMFormat nodes should call format_data directly
        return "LLMFormat tool should be used via format_data method, not execute"
    
    def format_data(self, data_list: List[str], prompt_template: str, format_style: str, user_context: str = "") -> str:
        """Use OpenAI to format the accumulated data with user context
        
        Args:
            data_list: List of raw data strings to format
            prompt_template: Custom formatting instruction (from caller)
            format_style: Output format (from caller) 
            user_context: Original user request (from caller)
        """
        try:
            # Combine all data into a single text
            combined_data = "\n".join(str(item) for item in data_list)
            
            # Create context-aware prompt with user's original request
            system_prompt = f"""You are a helpful assistant that converts raw data into human-readable {format_style} format.
            
            Guidelines:
            - Format: {format_style} (summary/report/list/paragraph)
            - Automatically detect the appropriate tone from the user's original request
            - If the user's request sounds casual/informal, respond casually
            - If the user's request sounds professional/formal, respond professionally  
            - If the user's request sounds technical, respond technically
            - Make it human-readable and conversational
            - Focus on key insights and important information
            - Use natural language, not raw data dumps
            - Reference the user's original request to make the response more contextual
            - CRITICAL: Detect the language of the user's original request and respond in the SAME language
            - If the user asked in Russian, respond in Russian
            - If the user asked in English, respond in English
            - If the user asked in any other language, respond in that language
            """
            
            user_prompt = f"""Original user request: "{user_context}"

            Task: {prompt_template}

            Raw data to format:
            {combined_data}

            Please convert this into a {format_style} that directly addresses the user's original request. 
            Automatically match the tone/style of their original question - if they asked casually, respond casually; 
            if formally, respond formally. Start by acknowledging what they asked for, then provide the information in a helpful and contextual way.

            IMPORTANT: Respond in the SAME language as the user's original request. If they asked in Russian, answer in Russian. 
            If they asked in English, answer in English."""

            response = OpenAIConfig.create_chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                use_case="formatting"
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"❌ LLM formatting failed: {str(e)}"
    
    def run(self, **kwargs) -> str:
        """Standard run interface"""
        return self.execute(kwargs) 