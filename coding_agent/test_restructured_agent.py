#!/usr/bin/env python3
"""
Test script for the restructured OverwatchAgent class.
This demonstrates the new workflow with human approval.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from overwatch_agent import OverwatchAgent


async def test_restructured_workflow():
    """Test the restructured OverwatchAgent workflow."""
    print("🧪 Testing Restructured OverwatchAgent Workflow")
    print("=" * 60)
    
    # Create agent instance
    agent = OverwatchAgent(
        app_name="test_overwatch_app",
        user_id="test_user"
    )
    
    # Test predefined request (bypasses voice input)
    test_request = "Create a simple Python calculator with basic operations"
    
    print(f"🎯 Testing with request: '{test_request}'")
    print("📋 This will demonstrate the new human approval step")
    print()
    
    try:
        # Run the complete workflow
        success = await agent.run_complete_workflow(
            user_request=test_request, 
            use_voice=False  # Skip voice input for testing
        )
        
        if success:
            print("\n🎉 Restructured workflow completed successfully!")
            print("✅ All new methods worked correctly:")
            print("   - get_project_goal() - captured user input")
            print("   - generate_and_review_plan() - generated plan and got approval")
            print("   - execute_plan() - executed tasks in dependency order")
        else:
            print("\n❌ Restructured workflow encountered errors.")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting restructured OverwatchAgent test...")
    asyncio.run(test_restructured_workflow())
