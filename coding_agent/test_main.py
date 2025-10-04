#!/usr/bin/env python3
"""
Test script for the coding agent without voice input.

This script tests the complete workflow using a predefined request
instead of requiring voice input, making it suitable for automated testing.
"""

import asyncio
import json
from typing import Dict, Any

# Import Google ADK components
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.runners import types
from google.genai.types import Content, Part

from src.agents.planner_agent import planner_agent
from src.agents.executor_agent import executor_agent


async def main():
    """
    Main async function that orchestrates the coding agent workflow.
    """
    print("🤖 Coding Agent Starting...")
    print("=" * 50)
    
    try:
        # Initialize the Runner and session service
        print("🔧 Initializing services...")
        session_service = InMemorySessionService()
        runner = Runner(
            app_name="coding_agent_app",
            agent=planner_agent,  # Use planner as the root agent
            session_service=session_service
        )
        
        print("✅ Services initialized successfully!")
        
        # Use predefined request instead of voice input
        user_request = "Build a simple Flask application with a single endpoint that returns hello world"
        print(f"\n🎯 Using predefined request: '{user_request}'")
        
        # Create a new session and store the user's request
        print("\n📋 Creating session...")
        session = await session_service.create_session(
            app_name="coding_agent_app",
            user_id="test_user"
        )
        session_id = session.id
        print(f"✅ Session created with ID: {session_id}")
        
        # Store initial state in session
        session.state.update({
            "user_request": user_request,
            "status": "planning",
            "current_task": None,
            "completed_tasks": [],
            "project_plan": None
        })
        
        # Run the planner agent to generate the project plan
        print("\n🧠 Running planner agent...")
        print("📊 Analyzing request and generating project plan...")
        
        try:
            # Create content for the planner
            planner_content = Content(
                parts=[Part.from_text(text=user_request)],
                role="user"
            )
            
            # Invoke the runner with the planner agent
            events = []
            async for event in runner.run_async(
                user_id="test_user",
                session_id=session_id,
                new_message=planner_content
            ):
                events.append(event)
                print(f"📄 Event: {event}")
            
            print("✅ Planner agent completed!")
            
            # Get the updated session to check for results
            updated_session = await session_service.get_session(
                app_name="coding_agent_app",
                user_id="test_user", 
                session_id=session_id
            )
            
            # Extract the project plan from the session state
            project_plan = updated_session.state.get("project_plan")
            
            if project_plan:
                print("\n🎉 Project plan generated successfully!")
                print("\n" + "="*60)
                print("📋 PROJECT PLAN")
                print("="*60)
                
                # Format and display the plan
                _display_project_plan(project_plan)
                
                # Update session state with the plan
                updated_session.state["project_plan"] = project_plan
                updated_session.state["status"] = "ready_for_execution"
                
            else:
                print("❌ No project plan found in session state.")
                print("🔍 Checking raw session state...")
                print(f"Session state keys: {list(updated_session.state.keys())}")
                
        except Exception as e:
            print(f"❌ Error running planner agent: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return
        
        print("\n🎯 Planning phase completed!")
        print("🚀 Starting task execution phase...")
        
        # Execute tasks in dependency order
        await _execute_tasks(runner, session_service, session_id, project_plan)
        
    except Exception as e:
        print(f"💥 Unexpected error in main function: {str(e)}")
        import traceback
        traceback.print_exc()


async def _execute_tasks(runner: Runner, session_service: InMemorySessionService, 
                        session_id: str, project_plan: Dict[str, Any]):
    """
    Execute tasks in dependency order using the executor agent.
    """
    tasks = project_plan.get('tasks', [])
    if not tasks:
        print("❌ No tasks to execute.")
        return
    
    completed_tasks = set()
    total_tasks = len(tasks)
    execution_round = 0
    
    print(f"\n🎯 Starting execution of {total_tasks} tasks...")
    print("=" * 60)
    
    while len(completed_tasks) < total_tasks:
        execution_round += 1
        print(f"\n🔄 Execution Round {execution_round}")
        print("-" * 30)
        
        # Find tasks that can be executed (dependencies met)
        executable_tasks = _find_executable_tasks(tasks, completed_tasks)
        
        if not executable_tasks:
            # Check for circular dependencies
            remaining_tasks = [task for task in tasks if task.get('task_id') not in completed_tasks]
            if remaining_tasks:
                print("❌ Circular dependency detected!")
                print("🔍 Remaining tasks that cannot be executed:")
                for task in remaining_tasks:
                    task_id = task.get('task_id', 'Unknown')
                    dependencies = task.get('dependencies', [])
                    missing_deps = [dep for dep in dependencies if dep not in completed_tasks]
                    print(f"   - {task_id}: Missing dependencies: {missing_deps}")
                print("\n💡 Please review the task dependencies and fix circular references.")
                return
            else:
                break
        
        # Execute the first available task
        current_task = executable_tasks[0]
        task_id = current_task.get('task_id', 'Unknown')
        
        print(f"🚀 Executing task: {task_id}")
        print(f"📝 Description: {current_task.get('description', 'No description')}")
        
        try:
            # Update session state with current task
            session_state = await session_service.get_session_state(session_id)
            session_state["current_task"] = current_task
            session_state["status"] = "executing"
            await session_service.update_session_state(session_id, session_state)
            
            # Execute the task using the executor agent
            print(f"\n🤖 ExecutorAgent starting task: {task_id}")
            print("=" * 50)
            
            # Stream the execution events
            events = await runner.run_async(
                agent=executor_agent,
                session_id=session_id,
                input_data={"task": current_task}
            )
            
            # Process and display events as they stream
            await _process_execution_events(events)
            
            # Mark task as completed
            completed_tasks.add(task_id)
            
            # Update session state
            session_state["completed_tasks"] = list(completed_tasks)
            session_state["current_task"] = None
            await session_service.update_session_state(session_id, session_state)
            
            print(f"\n✅ Task {task_id} completed successfully!")
            print(f"📊 Progress: {len(completed_tasks)}/{total_tasks} tasks completed")
            
        except Exception as e:
            print(f"❌ Error executing task {task_id}: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return
    
    print(f"\n🎉 All tasks completed successfully!")
    print(f"📊 Final progress: {len(completed_tasks)}/{total_tasks} tasks completed")
    
    # Update final session state
    session_state = await session_service.get_session_state(session_id)
    session_state["status"] = "completed"
    await session_service.update_session_state(session_id, session_state)


def _find_executable_tasks(tasks: list, completed_tasks: set) -> list:
    """
    Find tasks that can be executed (all dependencies are met).
    """
    executable = []
    
    for task in tasks:
        task_id = task.get('task_id')
        if task_id in completed_tasks:
            continue
            
        dependencies = task.get('dependencies', [])
        if all(dep in completed_tasks for dep in dependencies):
            executable.append(task)
    
    return executable


async def _process_execution_events(events):
    """
    Process and display execution events as they stream from the executor agent.
    """
    try:
        async for event in events:
            # Display different types of events
            if hasattr(event, 'type'):
                if event.type == 'thought':
                    print(f"💭 Agent thought: {event.content}")
                elif event.type == 'tool_call':
                    print(f"🔧 Tool call: {event.tool_name}")
                    if hasattr(event, 'tool_input'):
                        print(f"   Input: {event.tool_input}")
                elif event.type == 'tool_result':
                    print(f"📋 Tool result: {event.result}")
                elif event.type == 'response':
                    print(f"💬 Agent response: {event.content}")
                else:
                    print(f"📄 Event ({event.type}): {event.content}")
            else:
                # Fallback for events without type attribute
                print(f"📄 Event: {event}")
                
    except Exception as e:
        print(f"⚠️  Error processing events: {str(e)}")


def _display_project_plan(plan: Dict[str, Any]):
    """
    Display a formatted version of the project plan.
    """
    try:
        # Display project information
        print(f"📝 Project: {plan.get('project_name', 'Unnamed Project')}")
        print(f"📄 Description: {plan.get('description', 'No description provided')}")
        
        if plan.get('project_type'):
            print(f"🏗️  Type: {plan['project_type']}")
        
        if plan.get('tech_stack'):
            print(f"🛠️  Tech Stack: {', '.join(plan['tech_stack'])}")
        
        if plan.get('total_estimated_hours'):
            print(f"⏱️  Estimated Hours: {plan['total_estimated_hours']}")
        
        # Display tasks
        tasks = plan.get('tasks', [])
        if tasks:
            print(f"\n📋 Tasks ({len(tasks)} total):")
            print("-" * 40)
            
            for i, task in enumerate(tasks, 1):
                print(f"\n{i}. {task.get('task_id', f'Task {i}')}")
                print(f"   📝 {task.get('description', 'No description')}")
                
                if task.get('category'):
                    print(f"   🏷️  Category: {task['category']}")
                
                if task.get('priority'):
                    print(f"   ⚡ Priority: {task['priority']}")
                
                if task.get('estimated_hours'):
                    print(f"   ⏱️  Hours: {task['estimated_hours']}")
                
                if task.get('dependencies'):
                    print(f"   🔗 Dependencies: {', '.join(task['dependencies'])}")
        else:
            print("\n❌ No tasks found in the plan.")
            
    except Exception as e:
        print(f"❌ Error displaying project plan: {str(e)}")
        print("📄 Raw plan data:")
        print(json.dumps(plan, indent=2))


if __name__ == "__main__":
    """
    Entry point for the application.
    """
    print("🚀 Starting Coding Agent Test Application")
    print("=" * 50)
    
    try:
        # Run the main async function
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Application interrupted by user.")
    except Exception as e:
        print(f"\n💥 Application failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n👋 Coding Agent Test Application finished.")
