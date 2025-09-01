#!/usr/bin/env python3
"""
🧪 Ambient Preflight Ping Test

Simple test to verify ambient agent system is working.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.ambient.agent_injector import AgentInjector
from src.core.cursor_client import get_global_cursor_client
from src.core.base_wizard import BaseWizard

def test_ambient_ping():
    """Test ambient preflight ping functionality"""
    printer = BaseWizard()
    
    printer.print_info("🧪 Testing Ambient Preflight Ping...")
    
    try:
        # 1. Check cursor-agent availability
        client = get_global_cursor_client()
        if not client.available():
            printer.print_error("❌ cursor-agent not available")
            return False
        
        printer.print_success("✅ cursor-agent is available")
        
        # 2. Ensure session
        session_id = client.ensure_session()
        if not session_id:
            printer.print_error("❌ Failed to establish session")
            return False
        
        printer.print_success(f"✅ Session established: {session_id[:8]}...")
        
        # 3. Test agent injector ping
        injector = AgentInjector()
        response = injector.send_prompt("Ambient preflight ping")
        
        if not response or not response.strip():
            printer.print_error("❌ No response from ambient ping")
            return False
        
        printer.print_success("✅ Ambient ping successful!")
        printer.print_info(f"Response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        printer.print_error(f"❌ Ambient ping test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ambient_ping()
    sys.exit(0 if success else 1)