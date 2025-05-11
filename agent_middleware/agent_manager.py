import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import autogen
from .models import AgentConfig

# Set up logging
logger = logging.getLogger(__name__)

class AgentManager:
    def __init__(self, agents_dir: str, config_list: Optional[List[Dict[str, Any]]] = None):
        self.agents_dir = Path(agents_dir).resolve()  # Get absolute path
        self.config_list = config_list or [{"model": "gpt-3.5-turbo"}]
        self.agents: Dict[str, AgentConfig] = {}
        self.agent_instances: Dict[str, autogen.AssistantAgent] = {}
        
        # Create agents directory if it doesn't exist
        self.agents_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized AgentManager with agents directory: {self.agents_dir}")
    
    def _validate_agent_data(self, agent_data: Dict[str, Any], file_path: Path) -> bool:
        """Validate that the agent data contains all required fields."""
        required_fields = ['name', 'description', 'system_message', 'version', 'author']
        missing_fields = [field for field in required_fields if field not in agent_data]
        
        if missing_fields:
            logger.error(f"Agent file {file_path} is missing required fields: {missing_fields}")
            return False
        
        if 'capabilities' not in agent_data:
            agent_data['capabilities'] = []  # Set default empty capabilities
            logger.warning(f"Agent file {file_path} has no capabilities defined")
        
        return True
    
    def load_agents(self) -> None:
        """Load all JSON files from the agents directory and initialize AutoGen agents."""
        self.agents.clear()
        self.agent_instances.clear()
        
        logger.info(f"Searching for JSON files in: {self.agents_dir}")
        json_files = list(self.agents_dir.rglob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files") #: {[str(f) for f in json_files]}
        
        for json_file in json_files:
            try:
                logger.info(f"Processing JSON file: {json_file}")
                with open(json_file, 'r', encoding='utf-8') as f:
                    agent_data = json.load(f)
                
                if not self._validate_agent_data(agent_data, json_file):
                    continue
                
                # Calculate the relative path from agents_dir
                rel_path = json_file.relative_to(self.agents_dir)
                # Convert path to URL format (e.g., 'chat/assistant' from 'chat/assistant.json')
                endpoint_path = str(rel_path.with_suffix('')).replace('\\', '/')
                logger.info(f"Created endpoint path: {endpoint_path}")
                
                # Create agent config
                agent_config = AgentConfig(**agent_data)
                self.agents[endpoint_path] = agent_config
                logger.info(f"Added agent config for: {endpoint_path}")
                
                # Initialize AutoGen agent
                agent = autogen.AssistantAgent(
                    name=agent_config.name,
                    system_message=agent_config.system_message,
                    llm_config={"config_list": self.config_list},
                    description=agent_config.description,
                )
                self.agent_instances[endpoint_path] = agent
                logger.info(f"Initialized AutoGen agent for: {endpoint_path}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON file {json_file}: {str(e)}")
            except Exception as e:
                logger.error(f"Error loading {json_file}: {str(e)}")
        
        logger.info(f"Finished loading agents. Total agents loaded: {len(self.agents)}")
        logger.info(f"Available agents: {list(self.agents.keys())}")
        
        if not self.agents:
            logger.warning("No agents were loaded successfully!")
    
    def get_agent(self, agent_path: str) -> Optional[autogen.AssistantAgent]:
        """Get an agent instance by path."""
        return self.agent_instances.get(agent_path)
    
    def get_agent_config(self, agent_path: str) -> Optional[AgentConfig]:
        """Get an agent configuration by path."""
        return self.agents.get(agent_path)
    
    def list_agents(self) -> List[str]:
        """List all available agent paths."""
        return list(self.agents.keys()) 