"""
Decision Trees Module for Personal Agent

This module contains predefined decision trees for common scenarios.
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from .reasoning import DecisionOption, DecisionContext


class ScenarioType(Enum):
    """Enumeration of common scenario types."""
    SCHEDULING = "scheduling"
    PRIORITIZATION = "prioritization"
    RESOURCE_ALLOCATION = "resource_allocation"
    CONFLICT_RESOLUTION = "conflict_resolution"
    INFORMATION_RETRIEVAL = "information_retrieval"


@dataclass
class DecisionNode:
    """Represents a node in a decision tree."""
    id: str
    question: str
    options: List[Dict[str, Any]] = field(default_factory=list)  # List of {"text": str, "next_node": str}
    is_leaf: bool = False
    action: Optional[str] = None  # Action to take if this is a leaf node
    metadata: Dict[str, Any] = field(default_factory=dict)


class DecisionTree:
    """Represents a decision tree for a specific scenario."""

    def __init__(self, scenario_type: ScenarioType, name: str):
        """
        Initialize a decision tree.
        
        Args:
            scenario_type (ScenarioType): The type of scenario this tree handles
            name (str): The name of the decision tree
        """
        self.scenario_type = scenario_type
        self.name = name
        self.nodes: Dict[str, DecisionNode] = {}
        self.root_node_id: Optional[str] = None

    def add_node(self, node: DecisionNode) -> None:
        """
        Add a node to the decision tree.
        
        Args:
            node (DecisionNode): The node to add
        """
        self.nodes[node.id] = node

    def set_root(self, node_id: str) -> None:
        """
        Set the root node of the decision tree.
        
        Args:
            node_id (str): The ID of the root node
        """
        if node_id in self.nodes:
            self.root_node_id = node_id
        else:
            raise ValueError(f"Node with ID {node_id} not found in tree")

    def get_node(self, node_id: str) -> Optional[DecisionNode]:
        """
        Get a node by its ID.
        
        Args:
            node_id (str): The ID of the node to retrieve
            
        Returns:
            DecisionNode: The node, or None if not found
        """
        return self.nodes.get(node_id)

    def traverse(self, current_node_id: str = None, answers: List[str] = None) -> Optional[DecisionNode]:
        """
        Traverse the decision tree based on answers.
        
        Args:
            current_node_id (str): The current node ID (starts at root if None)
            answers (List[str]): List of answers to previous questions
            
        Returns:
            DecisionNode: The final node reached, or None if traversal failed
        """
        if current_node_id is None:
            current_node_id = self.root_node_id
        
        if current_node_id is None:
            return None
        
        node = self.get_node(current_node_id)
        if not node:
            return None
        
        # If this is a leaf node, return it
        if node.is_leaf:
            return node
        
        # If we don't have answers, we can't proceed further
        if not answers:
            return node
        
        # Find the next node based on the last answer
        last_answer = answers[-1].lower()
        for option in node.options:
            if option["text"].lower() == last_answer:
                return self.traverse(option["next_node"], answers[:-1])
        
        # If no matching option found, return current node
        return node


class DecisionTreeManager:
    """Manager for decision trees."""

    def __init__(self):
        """Initialize the decision tree manager."""
        self.trees: Dict[str, DecisionTree] = {}
        self._initialize_default_trees()

    def _initialize_default_trees(self) -> None:
        """Initialize default decision trees for common scenarios."""
        # Create a scheduling decision tree
        self._create_scheduling_tree()
        
        # Create a prioritization decision tree
        self._create_prioritization_tree()
        
        # Create a conflict resolution decision tree
        self._create_conflict_resolution_tree()

    def _create_scheduling_tree(self) -> None:
        """Create a decision tree for scheduling tasks."""
        tree = DecisionTree(ScenarioType.SCHEDULING, "Task Scheduling")
        
        # Create nodes
        node1 = DecisionNode(
            id="start",
            question="Is the task time-sensitive?",
            options=[
                {"text": "Yes", "next_node": "urgent"},
                {"text": "No", "next_node": "flexible"}
            ]
        )
        
        node2 = DecisionNode(
            id="urgent",
            question="Does the task have a fixed deadline?",
            options=[
                {"text": "Yes", "next_node": "deadline"},
                {"text": "No", "next_node": "asap"}
            ]
        )
        
        node3 = DecisionNode(
            id="flexible",
            question="Can the task be scheduled for later?",
            options=[
                {"text": "Yes", "next_node": "later"},
                {"text": "No", "next_node": "soon"}
            ]
        )
        
        node4 = DecisionNode(
            id="deadline",
            question="Is the deadline within 24 hours?",
            options=[
                {"text": "Yes", "next_node": "immediate"},
                {"text": "No", "next_node": "scheduled"}
            ]
        )
        
        # Leaf nodes
        node5 = DecisionNode(
            id="asap",
            question="",
            is_leaf=True,
            action="Schedule task for immediate execution",
            metadata={"priority": "high"}
        )
        
        node6 = DecisionNode(
            id="later",
            question="",
            is_leaf=True,
            action="Schedule task for next week",
            metadata={"priority": "low"}
        )
        
        node7 = DecisionNode(
            id="soon",
            question="",
            is_leaf=True,
            action="Schedule task for tomorrow",
            metadata={"priority": "medium"}
        )
        
        node8 = DecisionNode(
            id="immediate",
            question="",
            is_leaf=True,
            action="Schedule task for immediate execution",
            metadata={"priority": "critical"}
        )
        
        node9 = DecisionNode(
            id="scheduled",
            question="",
            is_leaf=True,
            action="Schedule task for the deadline date",
            metadata={"priority": "high"}
        )
        
        # Add nodes to tree
        for node in [node1, node2, node3, node4, node5, node6, node7, node8, node9]:
            tree.add_node(node)
        
        tree.set_root("start")
        self.trees["scheduling"] = tree

    def _create_prioritization_tree(self) -> None:
        """Create a decision tree for task prioritization."""
        tree = DecisionTree(ScenarioType.PRIORITIZATION, "Task Prioritization")
        
        # Create nodes
        node1 = DecisionNode(
            id="start",
            question="Is the task related to a critical project?",
            options=[
                {"text": "Yes", "next_node": "critical"},
                {"text": "No", "next_node": "non_critical"}
            ]
        )
        
        node2 = DecisionNode(
            id="critical",
            question="Does the task have an immediate impact?",
            options=[
                {"text": "Yes", "next_node": "immediate_impact"},
                {"text": "No", "next_node": "delayed_impact"}
            ]
        )
        
        node3 = DecisionNode(
            id="non_critical",
            question="Is the task time-sensitive?",
            options=[
                {"text": "Yes", "next_node": "time_sensitive"},
                {"text": "No", "next_node": "not_urgent"}
            ]
        )
        
        # Leaf nodes
        node4 = DecisionNode(
            id="immediate_impact",
            question="",
            is_leaf=True,
            action="Assign highest priority",
            metadata={"priority_level": 1}
        )
        
        node5 = DecisionNode(
            id="delayed_impact",
            question="",
            is_leaf=True,
            action="Assign high priority",
            metadata={"priority_level": 2}
        )
        
        node6 = DecisionNode(
            id="time_sensitive",
            question="",
            is_leaf=True,
            action="Assign medium priority",
            metadata={"priority_level": 3}
        )
        
        node7 = DecisionNode(
            id="not_urgent",
            question="",
            is_leaf=True,
            action="Assign low priority",
            metadata={"priority_level": 4}
        )
        
        # Add nodes to tree
        for node in [node1, node2, node3, node4, node5, node6, node7]:
            tree.add_node(node)
        
        tree.set_root("start")
        self.trees["prioritization"] = tree

    def _create_conflict_resolution_tree(self) -> None:
        """Create a decision tree for conflict resolution."""
        tree = DecisionTree(ScenarioType.CONFLICT_RESOLUTION, "Conflict Resolution")
        
        # Create nodes
        node1 = DecisionNode(
            id="start",
            question="Is the conflict between people or systems?",
            options=[
                {"text": "People", "next_node": "people_conflict"},
                {"text": "Systems", "next_node": "system_conflict"}
            ]
        )
        
        node2 = DecisionNode(
            id="people_conflict",
            question="Is the conflict urgent?",
            options=[
                {"text": "Yes", "next_node": "urgent_people"},
                {"text": "No", "next_node": "non_urgent_people"}
            ]
        )
        
        node3 = DecisionNode(
            id="system_conflict",
            question="Is data integrity at risk?",
            options=[
                {"text": "Yes", "next_node": "data_risk"},
                {"text": "No", "next_node": "no_data_risk"}
            ]
        )
        
        # Leaf nodes
        node4 = DecisionNode(
            id="urgent_people",
            question="",
            is_leaf=True,
            action="Escalate to mediator immediately",
            metadata={"escalation_level": "high"}
        )
        
        node5 = DecisionNode(
            id="non_urgent_people",
            question="",
            is_leaf=True,
            action="Schedule mediation session",
            metadata={"escalation_level": "low"}
        )
        
        node6 = DecisionNode(
            id="data_risk",
            question="",
            is_leaf=True,
            action="Halt affected systems and notify IT",
            metadata={"escalation_level": "critical"}
        )
        
        node7 = DecisionNode(
            id="no_data_risk",
            question="",
            is_leaf=True,
            action="Log issue and schedule review",
            metadata={"escalation_level": "medium"}
        )
        
        # Add nodes to tree
        for node in [node1, node2, node3, node4, node5, node6, node7]:
            tree.add_node(node)
        
        tree.set_root("start")
        self.trees["conflict_resolution"] = tree

    def get_tree(self, tree_id: str) -> Optional[DecisionTree]:
        """
        Get a decision tree by its ID.
        
        Args:
            tree_id (str): The ID of the tree to retrieve
            
        Returns:
            DecisionTree: The decision tree, or None if not found
        """
        return self.trees.get(tree_id)

    def get_tree_by_scenario(self, scenario_type: ScenarioType) -> Optional[DecisionTree]:
        """
        Get a decision tree by scenario type.
        
        Args:
            scenario_type (ScenarioType): The scenario type
            
        Returns:
            DecisionTree: The decision tree, or None if not found
        """
        for tree in self.trees.values():
            if tree.scenario_type == scenario_type:
                return tree
        return None

    def execute_tree(self, tree_id: str, answers: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Execute a decision tree and return the result.
        
        Args:
            tree_id (str): The ID of the tree to execute
            answers (List[str]): List of answers to guide the traversal
            
        Returns:
            Dict[str, Any]: The result of the tree execution, or None if failed
        """
        tree = self.get_tree(tree_id)
        if not tree:
            return None
        
        final_node = tree.traverse(answers=answers or [])
        if not final_node:
            return None
        
        return {
            "action": final_node.action,
            "metadata": final_node.metadata,
            "node_id": final_node.id
        }

    def list_trees(self) -> List[Dict[str, Any]]:
        """
        List all available decision trees.
        
        Returns:
            List[Dict[str, Any]]: List of tree information
        """
        return [
            {
                "id": tree_id,
                "name": tree.name,
                "scenario_type": tree.scenario_type.value
            }
            for tree_id, tree in self.trees.items()
        ]