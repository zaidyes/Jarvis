#!/usr/bin/env python3
"""
Run script for the Overwatch Agent application.

This script provides a simple entry point to start the OverwatchAgent
and run the complete coding agent workflow.
"""

import asyncio
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from overwatch_agent import OverwatchAgent


async def main():
    """Main function to run the Overwatch Agent."""
    print("🚀 Starting Overwatch Agent Application")
    print("=" * 50)
    
    try:
        # Create an instance of the OverwatchAgent
        agent = OverwatchAgent(
            app_name="overwatch_coding_agent",
            user_id="user"
        )
        
        # Start the project workflow
        success = await agent.start_project()
        
        if success:
            print("\n🎉 Project completed successfully!")
            print("✅ All tasks have been executed and the project is ready.")
        else:
            print("\n❌ Project execution encountered errors.")
            print("💡 Please review the output above for details.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Application interrupted by user.")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Application failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Overwatch Agent Application finished.")


if __name__ == "__main__":
    """
    Entry point for the application.
    """
    asyncio.run(main())
