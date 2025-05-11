from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field

class AgentRequest(BaseModel):
    message: str = Field(..., description="The message to send to the agent")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional context for the agent")

class AgentResponse(BaseModel):
    response: str = Field(..., description="The agent's response")
    context: Optional[Dict[str, Any]] = Field(None, description="Updated context from the agent")

class SimpleAgentConfig(BaseModel):
    name: str = Field(..., description="Name of the agent")
    description: str = Field(..., description="Description of the agent's capabilities")
    system_message: Optional[str] = Field(None, description="System message for the agent")
    capabilities: List[str] = Field(default_factory=list, description="List of agent capabilities")
    version: str = Field(..., description="Version of the agent")
    author: str = Field(..., description="Author of the agent")

class ComplexAgentConfig(BaseModel):
    provider: str = Field(..., description="Provider of the agent")
    component_type: str = Field(..., description="Type of component")
    version: int = Field(..., description="Version number")
    component_version: int = Field(..., description="Component version number")
    description: str = Field(..., description="Description of the agent")
    label: str = Field(..., description="Label for the agent")
    config: Dict[str, Any] = Field(..., description="Configuration details")

class AgentConfig(BaseModel):
    # Simple agent fields
    name: Optional[str] = Field(None, description="Name of the agent")
    description: str = Field(..., description="Description of the agent's capabilities")
    system_message: Optional[str] = Field(None, description="System message for the agent")
    capabilities: List[str] = Field(default_factory=list, description="List of agent capabilities")
    version: Union[str, int] = Field(..., description="Version of the agent")
    author: Optional[str] = Field(None, description="Author of the agent")
    
    # Complex agent fields
    provider: Optional[str] = Field(None, description="Provider of the agent")
    component_type: Optional[str] = Field(None, description="Type of component")
    component_version: Optional[int] = Field(None, description="Component version number")
    label: Optional[str] = Field(None, description="Label for the agent")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuration details")
    
    @property
    def display_name(self) -> str:
        """Get the display name of the agent."""
        return self.name or self.label or "Unnamed Agent"
    
    @property
    def display_description(self) -> str:
        """Get the display description of the agent."""
        return self.description

class AgentList(BaseModel):
    agents: List[str] = Field(..., description="List of available agent paths") 