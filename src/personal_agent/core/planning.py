"""
Planning Module for Personal Agent

This module contains functionality for breaking down complex tasks into subtasks
and managing task execution.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime


class TaskStatus(Enum):
    """Enumeration of task statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """Represents a single task or subtask."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    subtasks: List['Task'] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_subtask(self, subtask: 'Task') -> None:
        """Add a subtask to this task."""
        self.subtasks.append(subtask)

    def mark_completed(self, result: Any = None) -> None:
        """Mark this task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result

    def mark_failed(self, error: str = None) -> None:
        """Mark this task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        if error:
            self.metadata["error"] = error

    def is_completed(self) -> bool:
        """Check if this task is completed."""
        return self.status == TaskStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if this task has failed."""
        return self.status == TaskStatus.FAILED

    def get_all_subtasks(self) -> List['Task']:
        """Get all subtasks recursively."""
        all_subtasks = []
        for subtask in self.subtasks:
            all_subtasks.append(subtask)
            all_subtasks.extend(subtask.get_all_subtasks())
        return all_subtasks

    def get_pending_subtasks(self) -> List['Task']:
        """Get all pending subtasks."""
        return [task for task in self.get_all_subtasks() if task.status == TaskStatus.PENDING]

    def get_failed_subtasks(self) -> List['Task']:
        """Get all failed subtasks."""
        return [task for task in self.get_all_subtasks() if task.status == TaskStatus.FAILED]


class PlanningEngine:
    """Engine for creating and managing task plans."""

    def __init__(self):
        """Initialize the planning engine."""
        self.plans = {}

    def create_plan(self, task_description: str, user_id: str = None) -> Task:
        """
        Create a plan for a complex task by breaking it down into subtasks.
        
        Args:
            task_description (str): Description of the complex task
            user_id (str): ID of the user requesting the task
            
        Returns:
            Task: The root task representing the plan
        """
        # Create the root task
        root_task = Task(
            description=task_description,
            metadata={"user_id": user_id} if user_id else {}
        )
        
        # For now, we'll just create a placeholder plan
        # In a real implementation, this would use an LLM to break down the task
        self._decompose_task(root_task)
        
        # Store the plan
        self.plans[root_task.id] = root_task
        
        return root_task

    def _decompose_task(self, task: Task) -> None:
        """
        Decompose a task into subtasks.
        
        This is a placeholder implementation. In a real system, this would use
        an LLM to intelligently break down tasks.
        
        Args:
            task (Task): The task to decompose
        """
        # This is a simplified decomposition
        # In a real implementation, we would use the LLM to generate subtasks
        task.add_subtask(Task(description=f"Research information for: {task.description}"))
        task.add_subtask(Task(description=f"Execute main action for: {task.description}"))
        task.add_subtask(Task(description=f"Verify results of: {task.description}"))

    def get_plan(self, plan_id: str) -> Optional[Task]:
        """
        Retrieve a plan by its ID.
        
        Args:
            plan_id (str): The ID of the plan to retrieve
            
        Returns:
            Task: The plan, or None if not found
        """
        return self.plans.get(plan_id)

    def update_task_status(self, task_id: str, status: TaskStatus, result: Any = None) -> bool:
        """
        Update the status of a task.
        
        Args:
            task_id (str): The ID of the task to update
            status (TaskStatus): The new status
            result (Any): The result of the task (if completed)
            
        Returns:
            bool: True if the task was found and updated, False otherwise
        """
        # Find the task in all plans
        for plan in self.plans.values():
            task = self._find_task_in_plan(plan, task_id)
            if task:
                task.status = status
                if result is not None:
                    task.result = result
                if status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.now()
                return True
        return False

    def _find_task_in_plan(self, task: Task, task_id: str) -> Optional[Task]:
        """
        Find a task by its ID within a plan.
        
        Args:
            task (Task): The task to search in
            task_id (str): The ID of the task to find
            
        Returns:
            Task: The found task, or None if not found
        """
        if task.id == task_id:
            return task
        
        for subtask in task.subtasks:
            found = self._find_task_in_plan(subtask, task_id)
            if found:
                return found
        
        return None

    def get_pending_tasks(self) -> List[Task]:
        """
        Get all pending tasks across all plans.
        
        Returns:
            List[Task]: List of pending tasks
        """
        pending_tasks = []
        for plan in self.plans.values():
            if plan.status == TaskStatus.PENDING:
                pending_tasks.append(plan)
            pending_tasks.extend(plan.get_pending_subtasks())
        return pending_tasks

    def execute_plan(self, plan_id: str) -> bool:
        """
        Execute a plan by marking all tasks as completed.
        
        This is a placeholder implementation. In a real system, this would
        actually execute the tasks.
        
        Args:
            plan_id (str): The ID of the plan to execute
            
        Returns:
            bool: True if the plan was found and executed, False otherwise
        """
        plan = self.get_plan(plan_id)
        if not plan:
            return False
        
        # Mark all tasks as completed
        self._mark_all_completed(plan)
        return True

    def _mark_all_completed(self, task: Task) -> None:
        """
        Mark a task and all its subtasks as completed.
        
        Args:
            task (Task): The task to mark as completed
        """
        task.mark_completed("Task executed successfully")
        for subtask in task.subtasks:
            self._mark_all_completed(subtask)