"""
Agent Manager for Personal Agent

This module contains the AgentManager class that handles the lifecycle management of agents.
"""

import os
import signal
import sys
from typing import Dict, Optional, List
from ..config.settings import Config
from ..core.agent import Agent
from ..core.factory import ComponentFactory
from ..utils.logging import get_logger, log_exception


class AgentManager:
    """
    Manager class for handling the lifecycle of agents.
    """
    
    def __init__(self):
        """
        Initialize the agent manager.
        """
        self.agents: Dict[str, Agent] = {}
        self.config = Config.load()
        self.logger = get_logger()
        self.logger.info("AgentManager initialized")
    
    def create_agent(self, user_id: str = "default_user", 
                     config: Optional[Config] = None) -> Agent:
        """
        Create a new agent instance.
        
        Args:
            user_id (str): ID of the user for this agent
            config (Optional[Config]): Configuration to use for the agent
            
        Returns:
            Agent: Created agent instance
        """
        self.logger.info(f"Creating agent for user: {user_id}")
        
        # Use provided config or default
        agent_config = config or self.config
        
        # Create agent using factory
        agent = ComponentFactory.create_agent(user_id=user_id, config=agent_config)
        
        # Store agent
        self.agents[user_id] = agent
        
        self.logger.info(f"Agent created for user: {user_id}")
        return agent
    
    def get_agent(self, user_id: str) -> Optional[Agent]:
        """
        Get an existing agent by user ID.
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            Optional[Agent]: Agent instance if found, None otherwise
        """
        return self.agents.get(user_id)
    
    def remove_agent(self, user_id: str) -> bool:
        """
        Remove an agent from management.
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            bool: True if agent was removed, False if not found
        """
        if user_id in self.agents:
            self.logger.info(f"Removing agent for user: {user_id}")
            del self.agents[user_id]
            return True
        return False
    
    def list_agents(self) -> List[str]:
        """
        List all managed agent user IDs.
        
        Returns:
            List[str]: List of user IDs for managed agents
        """
        return list(self.agents.keys())
    
    def start_agent(self, user_id: str) -> Agent:
        """
        Start an agent (create if not exists, or return existing).
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            Agent: Agent instance
        """
        agent = self.get_agent(user_id)
        if not agent:
            agent = self.create_agent(user_id)
        
        self.logger.info(f"Agent started for user: {user_id}")
        return agent
    
    def stop_agent(self, user_id: str) -> bool:
        """
        Stop an agent (remove from management).
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            bool: True if agent was stopped, False if not found
        """
        return self.remove_agent(user_id)
    
    def stop_all_agents(self):
        """
        Stop all managed agents.
        """
        self.logger.info("Stopping all agents")
        user_ids = list(self.agents.keys())
        for user_id in user_ids:
            self.remove_agent(user_id)
        self.logger.info("All agents stopped")
    
    def get_agent_status(self, user_id: str) -> Dict[str, any]:
        """
        Get status information for an agent.
        
        Args:
            user_id (str): ID of the user
            
        Returns:
            Dict[str, any]: Status information
        """
        agent = self.get_agent(user_id)
        if not agent:
            return {"status": "not_found"}
        
        return {
            "status": "running",
            "user_id": user_id,
            "agent_name": agent.name,
            "agent_version": agent.version,
            "conversation_history_length": len(agent.conversation_history)
        }
    
    def get_all_agents_status(self) -> List[Dict[str, any]]:
        """
        Get status information for all agents.
        
        Returns:
            List[Dict[str, any]]: List of status information for all agents
        """
        return [self.get_agent_status(user_id) for user_id in self.list_agents()]
    
    def shutdown(self):
        """
        Shutdown the agent manager and all managed agents.
        """
        self.logger.info("Shutting down AgentManager")
        self.stop_all_agents()
        self.logger.info("AgentManager shutdown complete")


# Global instance for easy access
_agent_manager = None


def get_agent_manager() -> AgentManager:
    """
    Get the global agent manager instance.
    
    Returns:
        AgentManager: Global agent manager instance
    """
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager


def shutdown_agent_manager():
    """
    Shutdown the global agent manager instance.
    """
    global _agent_manager
    if _agent_manager is not None:
        _agent_manager.shutdown()
        _agent_manager = None


def signal_handler(sig, frame):
    """
    Signal handler for graceful shutdown.
    
    Args:
        sig: Signal number
        frame: Current stack frame
    """
    logger = get_logger()
    logger.info("\nReceived interrupt signal. Shutting down...")
    shutdown_agent_manager()
    sys.exit(0)


# Register signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)