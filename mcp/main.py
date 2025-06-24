"""Command-line tool to detect user intent using a local LLM."""

import argparse
import json
import subprocess
import sys

from .llm import answer_question, generate_shell_command, generate_patch, generate_script
from .recognizer import detect_intent, get_buffer_info


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect intent of a command")
    parser.add_argument("text", help="User command text")
    parser.add_argument("--full-response", action="store_true", help="Show full response instead of just intent")
    parser.add_argument("--provider", choices=["ollama", "openai"], help="LLM provider to use (default: from LLM_PROVIDER env var or 'ollama')")
    parser.add_argument("--openai-key", help="OpenAI API key (default: from OPENAI_API_KEY env var)")
    parser.add_argument("--model", help="Model to use with provider (default: from env var or provider default)")
    args = parser.parse_args()
    
    # Установка API ключа если указан
    if args.openai_key:
        import os
        os.environ["OPENAI_API_KEY"] = args.openai_key
        
    # Установка провайдера если указан
    if args.provider:
        import os
        os.environ["LLM_PROVIDER"] = args.provider
        
    # Установка модели если указана
    if args.model:
        import os
        provider = os.environ.get("LLM_PROVIDER", "ollama").lower()
        if provider == "ollama":
            os.environ["OLLAMA_MODEL"] = args.model
        elif provider == "openai":
            os.environ["OPENAI_MODEL"] = args.model
    
    # Detect user intent
    intent = detect_intent(args.text)
    
    if args.full_response:
        # Process the intent and get detailed response
        response = process_intent(intent, args.text)
        print(json.dumps(response, indent=2, ensure_ascii=False))
    else:
        # Just print the intent for compatibility with existing code
        print(intent)


def process_intent(intent: str, user_text: str) -> dict:
    """Process the detected intent and return appropriate response."""
    result = {"intent": intent, "success": True}
    
    try:
        if intent == "ask_question":
            result["response"] = answer_question(user_text)
            
        elif intent == "shell_command":
            cmd = generate_shell_command(user_text)
            result["command"] = cmd
            
        elif intent == "generate_script":
            script_info = generate_script(user_text)
            result["script"] = script_info
            
        elif intent == "modify_code":
            patch = generate_patch(user_text)
            result["patch"] = patch
            
        elif intent == "run_program":
            buffer_info = get_buffer_info(user_text)
            result["buffer_info"] = buffer_info
            
            # Attempt to run the buffer program if it exists
            try:
                cmd_parts = [buffer_info["command"]]
                
                # Add parameters if available
                params = buffer_info.get("parameters", {})
                for key, value in params.items():
                    cmd_parts.append(f"--{key}={value}")
                
                # Run the command and capture output
                proc = subprocess.run(
                    cmd_parts, 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                
                result["execution"] = {
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "command": " ".join(cmd_parts)
                }
                
                if proc.returncode != 0:
                    result["success"] = False
                    result["error"] = f"Program exited with code {proc.returncode}"
                    
            except FileNotFoundError:
                result["success"] = False
                result["error"] = f"Buffer program not found: {buffer_info['command']}"
                
            except subprocess.TimeoutExpired:
                result["success"] = False
                result["error"] = "Buffer program execution timed out after 10 seconds"
                
            except Exception as e:
                result["success"] = False
                result["error"] = f"Error executing buffer program: {str(e)}"
        
        else:
            result["success"] = False
            result["error"] = f"Unknown intent: {intent}"
            
    except Exception as e:
        result["success"] = False
        result["error"] = f"Error processing intent: {str(e)}"
    
    return result


if __name__ == "__main__":
    main()
