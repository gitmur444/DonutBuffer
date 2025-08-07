"""OpenAI configuration - centralized settings to avoid duplication"""

import openai

class OpenAIConfig:
    """Centralized OpenAI API configuration"""
    
    # Model settings
    DEFAULT_MODEL = "gpt-4o"
    
    # Temperature settings for different use cases
    PLANNING_TEMPERATURE = 0.1  # More deterministic for plan generation
    FORMATTING_TEMPERATURE = 0.3  # Slightly more creative for text formatting
    
    # Token limits
    PLANNING_MAX_TOKENS = 1000    # For plan generation
    FORMATTING_MAX_TOKENS = 500   # For text formatting
    
    @classmethod
    def create_chat_completion(cls, messages, use_case="planning"):
        """Create chat completion with appropriate settings
        
        Args:
            messages: List of message dicts for OpenAI API
            use_case: "planning" or "formatting" - determines temperature/tokens
        """
        
        if use_case == "planning":
            temperature = cls.PLANNING_TEMPERATURE
            max_tokens = cls.PLANNING_MAX_TOKENS
        elif use_case == "formatting":
            temperature = cls.FORMATTING_TEMPERATURE
            max_tokens = cls.FORMATTING_MAX_TOKENS
        else:
            # Default to planning settings
            temperature = cls.PLANNING_TEMPERATURE
            max_tokens = cls.PLANNING_MAX_TOKENS
        
        return openai.chat.completions.create(
            model=cls.DEFAULT_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        ) 