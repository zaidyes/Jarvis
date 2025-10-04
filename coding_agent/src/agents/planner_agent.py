"""
Planner Agent for breaking down high-level software development requests into structured project plans.

This module defines the PlannerAgent which uses Google ADK's LlmAgent to create
structured JSON plans from high-level software development requests. The agent
acts as an expert software architect to break down complex requirements into
manageable tasks with proper dependencies.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from google.adk.agents import LlmAgent


class Task(BaseModel):
    """
    Represents a single task in a software development project plan.
    
    This Pydantic model enforces structured JSON output for individual tasks,
    ensuring consistent task representation with proper dependencies and metadata.
    """
    task_id: str = Field(
        ...,
        description="Unique identifier for the task (e.g., 'task_001', 'setup_env')"
    )
    description: str = Field(
        ...,
        description="Detailed description of what needs to be accomplished in this task"
    )
    dependencies: List[str] = Field(
        default=[],
        description="List of task IDs that must be completed before this task can start"
    )
    estimated_hours: Optional[float] = Field(
        default=None,
        description="Estimated time to complete the task in hours"
    )
    priority: str = Field(
        default="medium",
        description="Priority level: 'low', 'medium', 'high', or 'critical'"
    )
    category: Optional[str] = Field(
        default=None,
        description="Category of the task (e.g., 'setup', 'backend', 'frontend', 'testing')"
    )


class Plan(BaseModel):
    """
    Represents a complete project plan with multiple tasks.
    
    This Pydantic model enforces structured JSON output for the entire project plan,
    ensuring consistent plan representation with proper task organization and metadata.
    """
    project_name: str = Field(
        ...,
        description="Name of the software project"
    )
    description: str = Field(
        ...,
        description="Brief description of the project and its objectives"
    )
    tasks: List[Task] = Field(
        ...,
        description="List of all tasks required to complete the project"
    )
    total_estimated_hours: Optional[float] = Field(
        default=None,
        description="Total estimated time to complete all tasks"
    )
    project_type: Optional[str] = Field(
        default=None,
        description="Type of project (e.g., 'web_app', 'api', 'desktop_app', 'mobile_app')"
    )
    tech_stack: Optional[List[str]] = Field(
        default=[],
        description="List of technologies and frameworks to be used"
    )


# Instantiate the LlmAgent for planning
planner_agent = LlmAgent(
    name="planner_agent",
    description="Expert software architect that breaks down high-level requests into structured project plans",
    instruction="""
    You are an expert software architect with 15+ years of experience in designing and planning software projects.
    
    Your role is to break down high-level software development requests into detailed, actionable project plans.
    
    When given a software development request, you should:
    1. Analyze the requirements and identify the core components needed
    2. Break down the project into logical, sequential tasks
    3. Identify dependencies between tasks to ensure proper execution order
    4. Estimate realistic time requirements for each task
    5. Categorize tasks by type (setup, backend, frontend, testing, deployment, etc.)
    6. Assign appropriate priority levels based on project criticality
    7. Suggest appropriate technology stacks when not specified
    8. Ensure the plan is comprehensive yet achievable
    
    Always structure your response as a complete project plan with:
    - Clear project identification and description
    - Detailed tasks with unique IDs and dependencies
    - Realistic time estimates
    - Proper task categorization and prioritization
    - Technology recommendations when appropriate
    
    Focus on creating plans that are:
    - Technically sound and industry-standard
    - Properly sequenced with clear dependencies
    - Realistic in scope and timeline
    - Comprehensive yet not overwhelming
    - Ready for immediate implementation
    
    Your expertise spans web applications, APIs, mobile apps, desktop applications, 
    microservices, databases, cloud deployment, and modern development practices.
    """,
    model="gemini-1.5-pro",
    output_schema=Plan
)
