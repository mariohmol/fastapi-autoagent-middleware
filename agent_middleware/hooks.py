from typing import Dict, List, Callable, Any
from fastapi import Request, Response

class HooksManager:
    def __init__(self):
        self.before_hooks: Dict[str, List[Callable]] = {}
        self.after_hooks: Dict[str, List[Callable]] = {}
    
    def add_before_hook(self, agent_path: str, hook: Callable[[Request, str], None]) -> None:
        """Add a hook to be executed before an agent is accessed."""
        if agent_path not in self.before_hooks:
            self.before_hooks[agent_path] = []
        self.before_hooks[agent_path].append(hook)
    
    def add_after_hook(self, agent_path: str, hook: Callable[[Request, Response, str, Any], None]) -> None:
        """Add a hook to be executed after an agent is accessed."""
        if agent_path not in self.after_hooks:
            self.after_hooks[agent_path] = []
        self.after_hooks[agent_path].append(hook)
    
    def execute_hooks(self, hooks: Dict[str, List[Callable]], path: str, *args) -> None:
        """Execute hooks for a given path, including wildcard matches."""
        # Execute exact path hooks
        if path in hooks:
            for hook in hooks[path]:
                hook(*args)
        
        # Execute wildcard hooks
        for hook_path, hook_list in hooks.items():
            if hook_path.endswith('*'):
                prefix = hook_path[:-1]
                if path.startswith(prefix):
                    for hook in hook_list:
                        hook(*args) 