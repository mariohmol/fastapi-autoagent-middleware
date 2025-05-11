import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List, Union
from fastapi import FastAPI, HTTPException, Request, Response, Body
from fastapi.routing import APIRouter
from pydantic import BaseModel
import autogen

from .models import AgentRequest, AgentResponse, AgentList, AgentConfig
from .hooks import HooksManager
from .agent_manager import AgentManager

# Set up logging
logger = logging.getLogger(__name__)

class AgentMiddleware:
    def __init__(
        self,
        app: FastAPI,
        agents_dir: str = "agents",
        base_path: str = "/agents",
        auto_reload: bool = False,
        config_list: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize the Agent Middleware.
        
        Args:
            app: FastAPI application instance
            agents_dir: Directory containing agent JSON files
            base_path: Base URL path for agent endpoints
            auto_reload: Whether to reload agents on each request
            config_list: List of configurations for AutoGen agents
        """
        self.app = app
        self.agents_dir = Path(agents_dir)
        self.base_path = base_path.rstrip("/")
        self.auto_reload = auto_reload
        
        # Initialize managers
        self.agent_manager = AgentManager(agents_dir, config_list)
        self.hooks_manager = HooksManager()
        
        # Create agents directory if it doesn't exist
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        
        # Load agents and create routes
        self.agent_manager.load_agents()
        self._create_routes()
    
    def add_before_hook(self, agent_path: str, hook: callable) -> None:
        """Add a hook to be executed before an agent is accessed."""
        self.hooks_manager.add_before_hook(agent_path, hook)
    
    def add_after_hook(self, agent_path: str, hook: callable) -> None:
        """Add a hook to be executed after an agent is accessed."""
        self.hooks_manager.add_after_hook(agent_path, hook)
    
    def _create_agent_endpoint(self, router: APIRouter, agent_path: str, agent_config: AgentConfig) -> None:
        """Create an endpoint for a specific agent."""
        endpoint_path = f"/{agent_path}/chat"
        logger.info(f"Creating endpoint for agent: {agent_path} at path: {endpoint_path}")
        
        @router.post(
            endpoint_path,
            response_model=AgentResponse,
            summary=f"Chat with {agent_config.display_name}",
            description=f"""
            Chat with the {agent_config.display_name} agent.
            
            **Capabilities:**
            {chr(10).join(f'- {cap}' for cap in agent_config.capabilities)}
            
            **Description:**
            {agent_config.display_description}
            
            **Version:** {agent_config.version}
            {f"**Author:** {agent_config.author}" if agent_config.author else ""}
            """,
            tags=[agent_path.split('/')[0]],  # Group by top-level directory
            operation_id=f"chat_with_{agent_path.replace('/', '_')}"
        )
        async def chat_with_agent(
            request: Request,
            chat_request: AgentRequest = Body(
                ...,
                description=f"Send a message to {agent_config.display_name}",
                example={
                    "message": "What can you help me with?",
                    "context": {"user_id": "123"}
                }
            )
        ):
            """Chat with a specific agent."""
            if self.auto_reload:
                self.agent_manager.load_agents()
            
            self.hooks_manager.execute_hooks(
                self.hooks_manager.before_hooks,
                agent_path,
                request,
                agent_path
            )
            
            agent = self.agent_manager.get_agent(agent_path)
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_path}' not found")
            
            # Create a user proxy agent for this chat
            user_proxy = autogen.UserProxyAgent(
                name="user",
                human_input_mode="NEVER",
                max_consecutive_auto_reply=1,
                is_termination_msg=lambda x: True,
                code_execution_config=False,
            )
            
            # Initialize the chat
            chat_response = user_proxy.initiate_chat(
                agent,
                message=chat_request.message,
                context=chat_request.context
            )
            
            # Extract the last message from the chat
            last_message = chat_response[-1]["content"] if chat_response else "No response from agent"
            
            response = AgentResponse(
                response=last_message,
                context=chat_request.context
            )
            
            self.hooks_manager.execute_hooks(
                self.hooks_manager.after_hooks,
                agent_path,
                request,
                response,
                agent_path,
                response
            )
            
            return response
    
    def _create_routes(self) -> None:
        """Create FastAPI routes for each agent."""
        router = APIRouter(
            prefix=self.base_path,
            tags=["agents"],
            responses={404: {"description": "Agent not found"}},
        )
        
        @router.get(
            "/",
            response_model=AgentList,
            summary="List all agents",
            description="Get a list of all available agent paths"
        )
        async def list_agents(request: Request):
            """List all available agents."""
            self.hooks_manager.execute_hooks(
                self.hooks_manager.before_hooks,
                "list",
                request,
                "list"
            )
            
            response = AgentList(agents=self.agent_manager.list_agents())
            
            self.hooks_manager.execute_hooks(
                self.hooks_manager.after_hooks,
                "list",
                request,
                response,
                "list",
                response
            )
            
            return response
        
        @router.get(
            "/{agent_path:path}",
            response_model=AgentConfig,
            summary="Get agent configuration",
            description="Get the configuration for a specific agent"
        )
        async def get_agent(request: Request, agent_path: str):
            """Get a specific agent's configuration."""
            if self.auto_reload:
                self.agent_manager.load_agents()
            
            self.hooks_manager.execute_hooks(
                self.hooks_manager.before_hooks,
                agent_path,
                request,
                agent_path
            )
            
            agent_config = self.agent_manager.get_agent_config(agent_path)
            if not agent_config:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_path}' not found")
            
            self.hooks_manager.execute_hooks(
                self.hooks_manager.after_hooks,
                agent_path,
                request,
                agent_config,
                agent_path,
                agent_config
            )
            
            return agent_config
        
        # Create individual endpoints for each agent
        logger.info(f"Creating endpoints for {len(self.agent_manager.agents)} agents")
        for agent_path, agent_config in self.agent_manager.agents.items():
            logger.info(f"Processing agent: {agent_path}")
            self._create_agent_endpoint(router, agent_path, agent_config)
        
        # Include the router in the app
        logger.info(f"Including router with {len(router.routes)} routes")
        self.app.include_router(router)
    
    def reload_agents(self) -> None:
        """Manually reload all agents."""
        self.agent_manager.load_agents() 