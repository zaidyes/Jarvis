"""
Overwatch Agent - Main orchestration class for the coding agent application.

This module contains the OverwatchAgent class that orchestrates the entire coding agent workflow:
1. Captures voice input from the user
2. Uses the planner agent to break down the request into a structured plan
3. Executes tasks using the executor agent
4. Manages the session state throughout the process
"""

import asyncio
import json
from typing import Dict, Any, Optional, List

# Import Google ADK components
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.runners import types
from google.genai.types import Content, Part

from agents.planner_agent import planner_agent
from agents.executor_agent import executor_agent
from tools.voice_input import get_voice_command


class OverwatchAgent:
    """
    Main orchestration class for the coding agent system.
    
    This class manages the entire workflow from voice input capture through
    task execution completion, providing centralized state management and
    error handling.
    """
    
    def __init__(self, app_name: str = "overwatch_agent_app", user_id: str = "default_user"):
        """
        Initialize the Overwatch Agent.
        
        Args:
            app_name: Name of the application for session management
            user_id: User ID for session management
        """
        self.app_name = app_name
        self.user_id = user_id
        self.plan: Optional[Dict[str, Any]] = None
        self.completed_tasks: List[str] = []
        self.session_id: Optional[str] = None
        self.runner: Optional[Runner] = None
        self.session_service: Optional[InMemorySessionService] = None
        
    def get_project_goal(self, use_voice: bool = True) -> str:
        """
        Get the project goal from the user via voice or text input with confirmation.
        
        Args:
            use_voice: Whether to attempt voice input first
            
        Returns:
            The captured user request (or None if cancelled)
        """
        while True:  # Loop until user confirms or cancels
            user_request = None
            
            if use_voice:
                print("\n🎤 Capturing voice input...")
                print("📝 Please speak your software development request clearly.")
                
                try:
                    user_request = get_voice_command()
                    print(f"\n🎯 Captured request: '{user_request}'")
                except Exception as e:
                    print(f"❌ Error capturing voice input: {str(e)}")
                    print("🔄 Falling back to text input...")
                    use_voice = False  # Disable voice for this attempt
            
            if not user_request:
                # Fallback to text input
                user_request = input("Please enter your software development request: ")
            
            # Confirmation step
            print("\n" + "="*60)
            print("📋 REQUEST CONFIRMATION")
            print("="*60)
            print(f"🎯 Jarvis heard: '{user_request}'")
            print("\nIs this correct?")
            print("  • Type 'y' or 'yes' to proceed with this request")
            print("  • Type 'n' or 'no' to try again")
            print("  • Type 'c' or 'cancel' to exit")
            
            confirmation = input("\nYour choice (y/n/c): ").strip().lower()
            
            if confirmation in ['y', 'yes']:
                print("✅ Request confirmed! Proceeding with project generation...")
                return user_request
            elif confirmation in ['c', 'cancel']:
                print("❌ Request cancelled by user.")
                print("👋 Goodbye!")
                return None
            elif confirmation in ['n', 'no']:
                print("🔄 Let's try again...")
                print("="*60)
                continue
            else:
                print("⚠️  Invalid choice. Please enter 'y' (yes), 'n' (no), or 'c' (cancel).")
                continue
        
    async def generate_and_review_plan(self, user_request: str) -> bool:
        """
        Generate a project plan using the PlannerAgent and get human approval.
        
        Args:
            user_request: The user's software development request
            
        Returns:
            True if plan is approved and ready for execution, False otherwise
        """
        print("\n🧠 Running planner agent...")
        print("📊 Analyzing request and generating project plan...")
        
        if not self.runner or not self.session_id:
            raise RuntimeError("Agent not properly initialized. Call initialize() and start_session() first.")
            
        try:
            # Create content for the planner
            planner_content = Content(
                parts=[Part.from_text(text=user_request)],
                role="user"
            )
            
            # Invoke the runner with the planner agent
            events = []
            project_plan = None
            
            async for event in self.runner.run_async(
                user_id=self.user_id,
                session_id=self.session_id,
                new_message=planner_content
            ):
                events.append(event)
                print(f"📄 Event: {event}")
                
                # Extract plan from event content if available
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                try:
                                    # Try to parse the JSON plan from the text
                                    import json
                                    plan_text = part.text.strip()
                                    if plan_text.startswith('{') and plan_text.endswith('}'):
                                        project_plan = json.loads(plan_text)
                                        print("✅ Plan extracted from event content!")
                                        break
                                except json.JSONDecodeError:
                                    continue
            
            print("✅ Planner agent completed!")
            
            # If we found a plan in the events, use it
            if project_plan:
                self.plan = project_plan
                
                # Store the plan in session state
                await self.update_session_state({"project_plan": project_plan})
                
                print("\n🎉 Project plan generated successfully!")
                self.display_project_plan(project_plan)
                
                # Ask for human approval
                print("\n" + "="*60)
                print("📋 PLAN APPROVAL REQUIRED")
                print("="*60)
                approval = input("Do you approve this plan? (y/n): ").strip().lower()
                
                if approval == 'y':
                    print("✅ Plan approved! Proceeding to execution...")
                    return True
                else:
                    print("❌ Plan not approved. Exiting...")
                    return False
            else:
                # Fallback: try to get from session state
                updated_session = await self.session_service.get_session(
                    app_name=self.app_name,
                    user_id=self.user_id, 
                    session_id=self.session_id
                )
                
                project_plan = updated_session.state.get("project_plan")
                
                if project_plan:
                    self.plan = project_plan
                    print("\n🎉 Project plan found in session state!")
                    self.display_project_plan(project_plan)
                    
                    # Ask for human approval
                    print("\n" + "="*60)
                    print("📋 PLAN APPROVAL REQUIRED")
                    print("="*60)
                    approval = input("Do you approve this plan? (y/n): ").strip().lower()
                    
                    if approval == 'y':
                        print("✅ Plan approved! Proceeding to execution...")
                        return True
                    else:
                        print("❌ Plan not approved. Exiting...")
                        return False
                else:
                    print("❌ No project plan found in session state.")
                    print("🔍 Checking raw session state...")
                    print(f"Session state keys: {list(updated_session.state.keys())}")
                    return False
                
        except Exception as e:
            print(f"❌ Error running planner agent: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
        
    async def execute_plan(self) -> bool:
        """
        Execute the approved plan by running tasks in dependency order.
        
        Returns:
            True if all tasks completed successfully, False otherwise
        """
        if not self.plan:
            print("❌ No plan available for execution.")
            return False
            
        tasks = self.plan.get('tasks', [])
        if not tasks:
            print("❌ No tasks to execute.")
            return False
        
        self.completed_tasks = []
        total_tasks = len(tasks)
        execution_round = 0
        
        print(f"\n🎯 Starting execution of {total_tasks} tasks...")
        print("=" * 60)
        
        while len(self.completed_tasks) < total_tasks:
            execution_round += 1
            print(f"\n🔄 Execution Round {execution_round}")
            print("-" * 30)
            
            # Find tasks that can be executed (dependencies met)
            executable_tasks = self.find_executable_tasks(tasks)
            
            if not executable_tasks:
                # Check for circular dependencies
                remaining_tasks = [task for task in tasks if task.get('task_id') not in self.completed_tasks]
                if remaining_tasks:
                    print("❌ Circular dependency detected!")
                    print("🔍 Remaining tasks that cannot be executed:")
                    for task in remaining_tasks:
                        task_id = task.get('task_id', 'Unknown')
                        dependencies = task.get('dependencies', [])
                        missing_deps = [dep for dep in dependencies if dep not in self.completed_tasks]
                        print(f"   - {task_id}: Missing dependencies: {missing_deps}")
                    print("\n💡 Please review the task dependencies and fix circular references.")
                    return False
                else:
                    break
            
            # Execute the first available task
            current_task = executable_tasks[0]
            task_id = current_task.get('task_id', 'Unknown')
            
            print(f"🚀 Executing task: {task_id}")
            print(f"📝 Description: {current_task.get('description', 'No description')}")
            
            try:
                # Update session state with current task
                await self.update_session_state({
                    "current_task": current_task,
                    "status": "executing"
                })
                
                # Execute the task using the executor agent
                success, final_output = await self.execute_single_task(current_task)
                
                if success:
                    # Mark task as completed
                    self.completed_tasks.append(task_id)
                    
                    # Update session state
                    await self.update_session_state({
                        "completed_tasks": self.completed_tasks.copy(),
                        "current_task": None
                    })
                    
                    # Print task completion summary
                    print(f"\n✅ Task {task_id} completed successfully!")
                    print(f"📊 Progress: {len(self.completed_tasks)}/{total_tasks} tasks completed")
                    
                    # Display task summary and pause for user control
                    print("\n" + "="*60)
                    print("📋 TASK COMPLETION SUMMARY")
                    print("="*60)
                    print(f"🎯 Task ID: {task_id}")
                    print(f"📝 Description: {current_task.get('description', 'No description')}")
                    print(f"🏷️  Category: {current_task.get('category', 'N/A')}")
                    print(f"⚡ Priority: {current_task.get('priority', 'N/A')}")
                    print(f"⏱️  Estimated Hours: {current_task.get('estimated_hours', 'N/A')}")
                    
                    # Show final output from ExecutorAgent
                    print(f"\n📋 Final Output from ExecutorAgent:")
                    print("-" * 40)
                    output_preview = final_output[:200] + "..." if len(final_output) > 200 else final_output
                    print(output_preview)
                    if len(final_output) > 200:
                        print(f"\n💡 Full output length: {len(final_output)} characters")
                    
                    # Show remaining tasks
                    remaining_tasks = total_tasks - len(self.completed_tasks)
                    if remaining_tasks > 0:
                        print(f"\n🔄 Remaining tasks: {remaining_tasks}")
                        print("📋 Next executable tasks:")
                        next_executable = self.find_executable_tasks(tasks)
                        for i, next_task in enumerate(next_executable[:3], 1):  # Show up to 3 next tasks
                            print(f"   {i}. {next_task.get('task_id', 'Unknown')}: {next_task.get('description', 'No description')[:50]}...")
                        if len(next_executable) > 3:
                            print(f"   ... and {len(next_executable) - 3} more tasks")
                    
                    # Pause for user control
                    print("\n" + "-"*60)
                    input("Press Enter to continue to the next task...")
                    print("-"*60)
                    
                else:
                    print(f"❌ Task {task_id} failed to execute.")
                    print("\n" + "="*60)
                    print("❌ TASK FAILURE SUMMARY")
                    print("="*60)
                    print(f"🎯 Task ID: {task_id}")
                    print(f"📝 Description: {current_task.get('description', 'No description')}")
                    print(f"🏷️  Category: {current_task.get('category', 'N/A')}")
                    print(f"⚡ Priority: {current_task.get('priority', 'N/A')}")
                    
                    # Future enhancement: Ask user how to proceed
                    print("\n💡 Future enhancement: This will ask the user how to proceed with task failures.")
                    print("   Options could include: retry, skip, abort, or modify the task.")
                    
                    return False
                    
            except Exception as e:
                print(f"❌ Error executing task {task_id}: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                return False
        
        print(f"\n🎉 All tasks completed successfully!")
        print(f"📊 Final progress: {len(self.completed_tasks)}/{total_tasks} tasks completed")
        
        # Provide instructions on how to access and run the generated application
        await self._provide_application_instructions()
        
        # Update final session state
        await self.update_session_state({"status": "completed"})
        return True
    
    async def _provide_application_instructions(self):
        """
        Analyze the generated project and provide instructions on how to access and run it.
        """
        print("\n" + "="*70)
        print("🚀 APPLICATION ACCESS INSTRUCTIONS")
        print("="*70)
        
        try:
            import os
            from src.tools.file_system_tools import list_files
            
            # List all projects in the output directory
            output_contents = list_files(".")
            
            if "Path does not exist" in output_contents or "Directory is empty" in output_contents:
                print("⚠️  No projects found in output directory.")
                print("💡 The application files may not have been created yet.")
                return
            
            print("📁 Generated Projects:")
            print(output_contents)
            
            # Try to detect the project type and provide specific instructions
            project_type, project_folder = await self._detect_project_type()
            
            if project_type:
                print(f"\n🎯 Detected Project Type: {project_type}")
                print(f"📁 Project Folder: {project_folder}")
                await self._provide_type_specific_instructions(project_type, project_folder)
            else:
                print("\n📋 General Instructions:")
                await self._provide_general_instructions()
                
        except Exception as e:
            print(f"❌ Error analyzing generated project: {str(e)}")
            await self._provide_general_instructions()
    
    async def _detect_project_type(self):
        """Detect the type of project based on generated files."""
        try:
            import os
            from src.tools.file_system_tools import list_files
            
            # Get list of directories in output folder
            output_contents = list_files(".")
            directories = []
            
            for line in output_contents.split('\n'):
                if '[DIR]' in line:
                    dir_name = line.split('[DIR]')[1].strip().rstrip('/')
                    if dir_name:  # Make sure it's not empty
                        directories.append(dir_name)
            
            # Check each directory for project type indicators
            for directory in directories:
                try:
                    contents = list_files(directory)
                    
                    # Check for web app files
                    if "index.html" in contents or "index.htm" in contents:
                        return "web_app", directory
                    
                    # Check for Python projects
                    if any(f.endswith('.py') for f in contents.split('\n') if '[FILE]' in f):
                        return "python_app", directory
                    
                    # Check for Node.js projects
                    if "package.json" in contents:
                        return "nodejs_app", directory
                        
                except:
                    continue
            
            return None, None
            
        except Exception:
            return None, None
    
    async def _provide_type_specific_instructions(self, project_type, project_folder):
        """Provide instructions specific to the detected project type."""
        
        if project_type == "web_app":
            print("\n🌐 Web Application Instructions:")
            print("-" * 40)
            print("📂 Your web application is ready!")
            print(f"📁 Location: output/{project_folder}/")
            print("\n🚀 How to run:")
            print("   1. Open your web browser")
            print(f"   2. Navigate to the project folder:")
            print(f"      cd output/{project_folder}")
            print("   3. Open index.html in your browser:")
            print("      open index.html")
            print("\n🔧 Alternative - Local Server:")
            print(f"   1. Navigate to project folder:")
            print(f"      cd output/{project_folder}")
            print("   2. Start a local server:")
            print("      python3 -m http.server 8000")
            print("   3. Open in browser:")
            print("      http://localhost:8000")
            
        elif project_type == "python_app":
            print("\n🐍 Python Application Instructions:")
            print("-" * 40)
            print("📂 Your Python application is ready!")
            print(f"📁 Location: output/{project_folder}/")
            print("\n🚀 How to run:")
            print(f"   1. Navigate to the project folder:")
            print(f"      cd output/{project_folder}")
            print("   2. Install dependencies (if any):")
            print("      pip install -r requirements.txt")
            print("   3. Run the application:")
            print("      python3 main.py")
            print("      # or")
            print("      python3 app.py")
            
        elif project_type == "nodejs_app":
            print("\n📦 Node.js Application Instructions:")
            print("-" * 40)
            print("📂 Your Node.js application is ready!")
            print(f"📁 Location: output/{project_folder}/")
            print("\n🚀 How to run:")
            print(f"   1. Navigate to the project folder:")
            print(f"      cd output/{project_folder}")
            print("   2. Install dependencies:")
            print("      npm install")
            print("   3. Run the application:")
            print("      npm start")
            print("      # or")
            print("      node index.js")
            
        else:
            await self._provide_general_instructions()
    
    async def _provide_general_instructions(self):
        """Provide general instructions for accessing generated projects."""
        print("\n📋 General Instructions:")
        print("-" * 40)
        print("📂 Your application has been generated!")
        print("\n🚀 How to access:")
        print("   1. Navigate to the output directory:")
        print("      cd output/")
        print("   2. Look for your project folder")
        print("   3. Check the files in the project folder")
        print("   4. Look for README files or main entry points")
        print("\n💡 Common entry points:")
        print("   • index.html (web applications)")
        print("   • main.py, app.py (Python applications)")
        print("   • package.json (Node.js applications)")
        print("   • README.md (project documentation)")
        
        print("\n" + "="*70)
        print("🎉 Your application is ready to use!")
        print("="*70)
        
    async def start_project(self, use_voice: bool = True) -> bool:
        """
        High-level method to start and run the complete project workflow.
        
        This method orchestrates the entire process:
        1. Get project goal from user
        2. Generate and review plan (with human approval)
        3. Execute the approved plan
        
        Args:
            use_voice: Whether to attempt voice input first
            
        Returns:
            True if project completed successfully, False otherwise
        """
        try:
            print("🤖 Overwatch Agent Starting Project Workflow...")
            print("=" * 60)
            
            # Initialize services
            await self.initialize()
            
            # Step 1: Get project goal from user
            print("\n📋 Step 1: Getting Project Goal")
            print("-" * 40)
            user_request = self.get_project_goal(use_voice=use_voice)
            
            if user_request is None:
                print("❌ Request cancelled by user. Exiting.")
                return False
            
            if not user_request.strip():
                print("❌ No request provided. Exiting.")
                return False
            
            # Start session
            await self.start_session(user_request)
            
            # Step 2: Generate and review plan
            print("\n🧠 Step 2: Generating and Reviewing Plan")
            print("-" * 40)
            plan_approved = await self.generate_and_review_plan(user_request)
            
            if not plan_approved:
                print("❌ Plan not approved or failed to generate.")
                return False
            
            # Step 3: Execute the approved plan
            print("\n🚀 Step 3: Executing Plan")
            print("-" * 40)
            success = await self.execute_plan()
            
            if success:
                print("\n🎉 Project workflow completed successfully!")
                print("✅ All tasks have been executed.")
            else:
                print("\n❌ Project execution encountered errors.")
                
            return success
            
        except Exception as e:
            print(f"💥 Unexpected error in project workflow: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
    async def initialize(self):
        """Initialize the Runner and session service."""
        print("🔧 Initializing Overwatch Agent services...")
        
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            app_name=self.app_name,
            agent=planner_agent,  # Use planner as the root agent
            session_service=self.session_service
        )
        
        print("✅ Overwatch Agent services initialized successfully!")
        
    async def start_session(self, user_request: str) -> str:
        """
        Start a new session and store the user's request.
        
        Args:
            user_request: The user's software development request
            
        Returns:
            Session ID of the created session
        """
        print(f"\n📋 Starting new session for request: '{user_request}'")
        
        if not self.session_service:
            raise RuntimeError("Session service not initialized. Call initialize() first.")
            
        # Create a new session
        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=self.user_id
        )
        self.session_id = session.id
        
        # Initialize session state
        self.session_state = {
            "user_request": user_request,
            "status": "planning",
            "current_task": None,
            "completed_tasks": [],
            "project_plan": None
        }
        
        # Store state in session
        session.state.update(self.session_state)
        
        print(f"✅ Session created with ID: {self.session_id}")
        return self.session_id
        
        
            
        
    async def execute_single_task(self, task: Dict[str, Any]) -> tuple[bool, str]:
        """
        Execute a single task using the executor agent.
        
        Args:
            task: Task dictionary containing task details
            
        Returns:
            Tuple of (success: bool, final_output: str)
        """
        task_id = task.get('task_id', 'Unknown')
        
        print(f"\n🤖 ExecutorAgent starting task: {task_id}")
        print("=" * 50)
        
        try:
            # Create content for the executor
            task_content = Content(
                parts=[Part.from_text(text=f"Execute task: {task_id}\nDescription: {task.get('description', '')}")],
                role="user"
            )
            
            # Execute the task using the runner
            events = []
            final_output = ""
            
            async for event in self.runner.run_async(
                user_id=self.user_id,
                session_id=self.session_id,
                new_message=task_content
            ):
                events.append(event)
                await self.process_execution_event(event)
                
                # Capture final output from agent responses
                if hasattr(event, 'type') and event.type == 'response':
                    final_output += str(event.content) + "\n"
                elif hasattr(event, 'content'):
                    final_output += str(event.content) + "\n"
            
            print(f"\n✅ Task {task_id} execution completed!")
            
            # Store the final output in the task for summary display
            task['final_output'] = final_output.strip() if final_output.strip() else "No detailed output captured"
            
            return True, final_output.strip()
            
        except Exception as e:
            print(f"❌ Error executing task {task_id}: {str(e)}")
            return False, f"Error: {str(e)}"
            
    async def process_execution_event(self, event):
        """Process and display execution events from the executor agent."""
        try:
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
            
    def find_executable_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find tasks that can be executed (all dependencies are met).
        
        Args:
            tasks: List of all tasks
            
        Returns:
            List of tasks that can be executed
        """
        executable = []
        
        for task in tasks:
            task_id = task.get('task_id')
            if task_id in self.completed_tasks:
                continue
                
            dependencies = task.get('dependencies', [])
            if all(dep in self.completed_tasks for dep in dependencies):
                executable.append(task)
        
        return executable
        
    async def update_session_state(self, state_delta: Dict[str, Any]):
        """
        Update the session state with new values.
        
        Args:
            state_delta: Dictionary of state updates to apply
        """
        if not self.session_service or not self.session_id:
            return
            
        # Update local state
        self.session_state.update(state_delta)
        
        # Update session in service
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=self.user_id,
            session_id=self.session_id
        )
        
        if session:
            session.state.update(state_delta)
            
    def display_project_plan(self, plan: Dict[str, Any]):
        """
        Display a formatted version of the project plan.
        
        Args:
            plan: The project plan dictionary containing project details and tasks.
        """
        try:
            print("\n" + "="*60)
            print("📋 PROJECT PLAN")
            print("="*60)
            
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
            
    async def run_complete_workflow(self, user_request: Optional[str] = None, use_voice: bool = True) -> bool:
        """
        Run the complete coding agent workflow.
        
        Args:
            user_request: Optional predefined request. If None, will capture input from user.
            use_voice: Whether to attempt voice input first
            
        Returns:
            True if workflow completed successfully, False otherwise
        """
        try:
            print("🤖 Overwatch Agent Starting...")
            print("=" * 50)
            
            # Initialize services
            await self.initialize()
            
            # Get user request
            if not user_request:
                user_request = self.get_project_goal(use_voice=use_voice)
            
            if not user_request.strip():
                print("❌ No request provided. Exiting.")
                return False
            
            # Start session
            await self.start_session(user_request)
            
            # Generate and review plan (with human approval)
            plan_approved = await self.generate_and_review_plan(user_request)
            if not plan_approved:
                print("❌ Plan not approved or failed to generate.")
                return False
            
            print("\n🎯 Planning phase completed!")
            print("🚀 Starting task execution phase...")
            
            # Execute approved plan
            success = await self.execute_plan()
            
            if success:
                print("\n🎉 Complete workflow finished successfully!")
            else:
                print("\n❌ Workflow completed with errors.")
                
            return success
            
        except Exception as e:
            print(f"💥 Unexpected error in workflow: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """
    Main entry point for running the Overwatch Agent.
    
    This function creates an instance of the OverwatchAgent and runs
    the complete workflow.
    """
    # Create and run the Overwatch Agent
    agent = OverwatchAgent()
    
    # For testing, use a predefined request instead of voice input
    test_request = "Build a simple Flask application with a single endpoint that returns hello world"
    success = await agent.run_complete_workflow(user_request=test_request, use_voice=False)
    
    if success:
        print("\n🎉 Overwatch Agent completed successfully!")
    else:
        print("\n❌ Overwatch Agent encountered errors.")


if __name__ == "__main__":
    """
    Entry point for the application.
    """
    print("🚀 Starting Overwatch Agent Application")
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
        print("\n👋 Overwatch Agent Application finished.")