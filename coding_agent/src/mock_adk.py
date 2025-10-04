"""
Mock implementation of Google ADK components for testing purposes.

This module provides mock implementations of the Google ADK classes
to allow testing of the coding agent workflow without requiring
the actual Google ADK installation.
"""

import asyncio
import json
from typing import Dict, Any, List, Optional
import uuid


class MockLlmAgent:
    """Mock implementation of LlmAgent for testing."""
    
    def __init__(self, instruction: str = "", model: str = "mock-model", 
                 output_schema=None, tools: List = None):
        self.instruction = instruction
        self.model = model
        self.output_schema = output_schema
        self.tools = tools or []
    
    async def run(self, input_data: Dict[str, Any], session_id: str = None):
        """Mock run method that simulates agent execution."""
        if "request" in input_data:
            # Simulate planner agent
            return await self._simulate_planner(input_data["request"])
        elif "task" in input_data:
            # Simulate executor agent
            return await self._simulate_executor(input_data["task"])
        else:
            return {"error": "Unknown input type"}
    
    async def _simulate_planner(self, request: str):
        """Simulate planner agent creating a project plan."""
        # Create a mock project plan based on the request
        if "flask" in request.lower():
            return {
                "project_name": "Flask Hello World App",
                "description": "A simple Flask application with a hello world endpoint",
                "project_type": "web_app",
                "tech_stack": ["Python", "Flask"],
                "total_estimated_hours": 2.0,
                "tasks": [
                    {
                        "task_id": "setup_project",
                        "description": "Create project structure and requirements.txt",
                        "dependencies": [],
                        "estimated_hours": 0.5,
                        "priority": "high",
                        "category": "setup"
                    },
                    {
                        "task_id": "create_app",
                        "description": "Create main Flask application file with hello world endpoint",
                        "dependencies": ["setup_project"],
                        "estimated_hours": 1.0,
                        "priority": "high",
                        "category": "backend"
                    },
                    {
                        "task_id": "test_app",
                        "description": "Test the Flask application",
                        "dependencies": ["create_app"],
                        "estimated_hours": 0.5,
                        "priority": "medium",
                        "category": "testing"
                    }
                ]
            }
        else:
            return {
                "project_name": "Generic Project",
                "description": f"Project based on request: {request}",
                "project_type": "application",
                "tech_stack": ["Python"],
                "total_estimated_hours": 1.0,
                "tasks": [
                    {
                        "task_id": "create_project",
                        "description": f"Create project based on: {request}",
                        "dependencies": [],
                        "estimated_hours": 1.0,
                        "priority": "high",
                        "category": "development"
                    }
                ]
            }
    
    async def _simulate_executor(self, task: Dict[str, Any]):
        """Simulate executor agent executing a task."""
        task_id = task.get("task_id", "unknown")
        description = task.get("description", "")
        
        # Simulate different task executions
        if task_id == "setup_project":
            return await self._execute_setup_project()
        elif task_id == "create_app":
            return await self._execute_create_app()
        elif task_id == "test_app":
            return await self._execute_test_app()
        else:
            return await self._execute_generic_task(task)
    
    async def _execute_setup_project(self):
        """Simulate setting up project structure."""
        import os
        
        # Create requirements.txt
        requirements_content = "Flask==2.3.3\n"
        os.makedirs("generated_project", exist_ok=True)
        
        with open("generated_project/requirements.txt", "w") as f:
            f.write(requirements_content)
        
        return {
            "status": "completed",
            "message": "Project structure created successfully",
            "files_created": ["requirements.txt"]
        }
    
    async def _execute_create_app(self):
        """Simulate creating the Flask app."""
        import os
        
        app_content = '''from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/health')
def health_check():
    return {'status': 'healthy'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
        
        os.makedirs("generated_project", exist_ok=True)
        
        with open("generated_project/app.py", "w") as f:
            f.write(app_content)
        
        return {
            "status": "completed",
            "message": "Flask application created successfully",
            "files_created": ["app.py"]
        }
    
    async def _execute_test_app(self):
        """Simulate testing the Flask app."""
        test_content = '''import unittest
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_hello_world(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), 'Hello, World!')
    
    def test_health_check(self):
        response = self.app.get('/health')
        self.assertEqual(response.status_code, 200)
        self.assertIn('healthy', response.get_json()['status'])

if __name__ == '__main__':
    unittest.main()
'''
        
        os.makedirs("generated_project", exist_ok=True)
        
        with open("generated_project/test_app.py", "w") as f:
            f.write(test_content)
        
        return {
            "status": "completed",
            "message": "Test file created successfully",
            "files_created": ["test_app.py"]
        }
    
    async def _execute_generic_task(self, task: Dict[str, Any]):
        """Simulate executing a generic task."""
        import os
        
        task_id = task.get("task_id", "generic_task")
        description = task.get("description", "Generic task execution")
        
        os.makedirs("generated_project", exist_ok=True)
        
        # Create a simple file for the task
        filename = f"{task_id}.txt"
        content = f"Task: {task_id}\nDescription: {description}\nStatus: Completed"
        
        with open(f"generated_project/{filename}", "w") as f:
            f.write(content)
        
        return {
            "status": "completed",
            "message": f"Task {task_id} completed successfully",
            "files_created": [filename]
        }


class MockRunner:
    """Mock implementation of Runner for testing."""
    
    def __init__(self, session_service=None):
        self.session_service = session_service
    
    async def run_async(self, agent, session_id: str = None, input_data: Dict[str, Any] = None):
        """Mock run_async method that simulates agent execution."""
        # Simulate agent execution
        result = await agent.run(input_data or {}, session_id)
        
        # Update session state with the result
        if self.session_service and session_id:
            session_state = await self.session_service.get_session_state(session_id)
            if "request" in input_data:
                # Planner agent result
                session_state["project_plan"] = result
            elif "task" in input_data:
                # Executor agent result
                session_state["last_task_result"] = result
            
            await self.session_service.update_session_state(session_id, session_state)
        
        # Return mock events
        return self._create_mock_events(result)
    
    def _create_mock_events(self, result: Dict[str, Any]):
        """Create mock events for streaming."""
        events = [
            MockEvent("thought", "Analyzing the request..."),
            MockEvent("tool_call", "Executing task"),
            MockEvent("tool_result", json.dumps(result)),
            MockEvent("response", "Task completed successfully")
        ]
        
        async def event_generator():
            for event in events:
                yield event
                await asyncio.sleep(0.1)  # Simulate processing time
        
        return event_generator()


class MockEvent:
    """Mock implementation of events."""
    
    def __init__(self, event_type: str, content: str):
        self.type = event_type
        self.content = content


class MockSessionService:
    """Mock implementation of InMemorySessionService for testing."""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    async def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "user_request": None,
            "status": "created",
            "current_task": None,
            "completed_tasks": [],
            "project_plan": None
        }
        return session_id
    
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get the current state of a session."""
        return self.sessions.get(session_id, {})
    
    async def update_session_state(self, session_id: str, state: Dict[str, Any]):
        """Update the state of a session."""
        if session_id in self.sessions:
            self.sessions[session_id].update(state)


# Mock the Google ADK imports
import sys
from unittest.mock import MagicMock

# Create mock modules
google_mock = MagicMock()
google_mock.adk = MagicMock()
google_mock.adk.agents = MagicMock()
google_mock.adk.session = MagicMock()

# Set up the mock classes
google_mock.adk.agents.LlmAgent = MockLlmAgent
google_mock.adk.agents.Runner = MockRunner
google_mock.adk.session.InMemorySessionService = MockSessionService

# Add to sys.modules
sys.modules['google'] = google_mock
sys.modules['google.adk'] = google_mock.adk
sys.modules['google.adk.agents'] = google_mock.adk.agents
sys.modules['google.adk.session'] = google_mock.adk.session
