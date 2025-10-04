#!/usr/bin/env python3
"""
Test script for the enhanced execute_plan() method with pause functionality.
This demonstrates the new user-controlled execution flow.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from overwatch_agent import OverwatchAgent


async def test_enhanced_execution():
    """Test the enhanced execute_plan method with pause functionality."""
    print("🧪 Testing Enhanced Execute Plan with Pause Functionality")
    print("=" * 70)
    
    # Create agent instance
    agent = OverwatchAgent(
        app_name="test_enhanced_execution",
        user_id="test_user"
    )
    
    # Test with a request that will generate multiple tasks
    test_request = "Create a simple Python web application with Flask, including a home page, about page, and contact form"
    
    print(f"🎯 Testing with request: '{test_request}'")
    print("📋 This will demonstrate:")
    print("   - Task completion summaries")
    print("   - Final output display from ExecutorAgent")
    print("   - User-controlled pause between tasks")
    print("   - Preview of next executable tasks")
    print()
    
    try:
        # Run the complete workflow
        success = await agent.run_complete_workflow(
            user_request=test_request, 
            use_voice=False  # Skip voice input for testing
        )
        
        if success:
            print("\n🎉 Enhanced execution workflow completed successfully!")
            print("✅ New features demonstrated:")
            print("   - Task completion summaries with detailed info")
            print("   - Final output capture and display from ExecutorAgent")
            print("   - User-controlled pause between tasks")
            print("   - Preview of upcoming tasks")
            print("   - Progress tracking with remaining task count")
        else:
            print("\n❌ Enhanced execution workflow encountered errors.")
            
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting enhanced execution test...")
    print("💡 Note: You'll be prompted to press Enter after each task completion")
    print("   This gives you control over the execution pace.")
    print()
    asyncio.run(test_enhanced_execution())
