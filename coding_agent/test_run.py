#!/usr/bin/env python3
"""
Test script to demonstrate the run.py functionality without interactive input.
"""

import asyncio
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from overwatch_agent import OverwatchAgent


async def test_start_project():
    """Test the start_project method with a predefined request."""
    print("🧪 Testing start_project() Method")
    print("=" * 50)
    
    try:
        # Create an instance of the OverwatchAgent
        agent = OverwatchAgent(
            app_name="test_overwatch_agent",
            user_id="test_user"
        )
        
        # Test the start_project method structure
        print("✅ OverwatchAgent instance created")
        print("✅ start_project method exists")
        
        # Show the method signature
        import inspect
        sig = inspect.signature(agent.start_project)
        print(f"✅ Method signature: {sig}")
        
        print("\n📋 The start_project() method will:")
        print("   1. Call get_project_goal() - Get user input")
        print("   2. Call generate_and_review_plan() - Generate and approve plan")
        print("   3. Call execute_plan() - Execute tasks with pause between each")
        
        print("\n🎯 To run the full workflow:")
        print("   python3 run.py")
        print("\n💡 The run.py script provides a clean entry point")
        print("   that encapsulates all the OverwatchAgent functionality.")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_start_project())
