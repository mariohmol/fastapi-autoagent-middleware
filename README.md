# FastAPI Agent Middleware

A middleware plugin for FastAPI that automatically exposes JSON agent files as API endpoints.

## Installation

You can install the package using pip:

```bash
pip install fastapi-agent-middleware
```

Or install directly from the source:

```bash
pip install git+https://github.com/mariohmol/fastapi-agent-middleware.git
```

## Features

- Automatically loads JSON agent files from a specified directory
- Creates REST endpoints based on the file structure
- Supports nested directories
- Optional auto-reload functionality
- Simple and easy to integrate
- Before and after hooks for custom processing
- Wildcard path support for hooks

## Quick Start

1. Create your agent JSON files in an `agents` directory:

```
agents/
├── chat/
│   └── assistant.json  # Will be available at /agents/chat/assistant
└── tasks/
    └── reminder.json   # Will be available at /agents/tasks/reminder
```

2. Integrate the middleware into your FastAPI application:

```python
from fastapi import FastAPI
from agent_middleware import AgentMiddleware

app = FastAPI()
agent_middleware = AgentMiddleware(
    app=app,
    agents_dir="agents",
    base_path="/agents",
    auto_reload=True
)
```

## Hooks

The middleware supports before and after hooks that can be used to add custom processing to agent requests:

### Before Hooks

Before hooks are executed before an agent is accessed. They receive the request and agent path:

```python
def my_before_hook(request: Request, agent_path: str):
    # Do something before the agent is accessed
    pass

# Add the hook
agent_middleware.add_before_hook("chat/*", my_before_hook)  # Apply to all chat agents
```

### After Hooks

After hooks are executed after an agent is accessed. They receive the request, response, agent path, and agent data:

```python
def my_after_hook(request: Request, response: Response, agent_path: str, agent_data: dict):
    # Do something after the agent is accessed
    pass

# Add the hook
agent_middleware.add_after_hook("tasks/*", my_after_hook)  # Apply to all task agents
```

### Wildcard Support

Hooks support wildcard paths using the `*` character:

- `"chat/*"` - Matches all agents under the chat directory
- `"*"` - Matches all agents
- `"tasks/reminder*"` - Matches all agents starting with "reminder" in the tasks directory

## API Endpoints

- `GET /agents/` - List all available agents
- `GET /agents/{agent_path}` - Get a specific agent by path

## Configuration Options

The `AgentMiddleware` class accepts the following parameters:

- `app`: FastAPI application instance
- `agents_dir`: Directory containing agent JSON files (default: "agents")
- `base_path`: Base URL path for agent endpoints (default: "/agents")
- `auto_reload`: Whether to reload agents on each request (default: False)

## Development

To set up the development environment:

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fastapi-agent-middleware.git
cd fastapi-agent-middleware
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Example

See `example_app.py` for a complete example of how to use the middleware, including examples of:
- Logging access to agents
- Measuring request timing
- Adding metadata to responses
- Using wildcard paths for hooks

## Running the Example

```bash
python example_app.py
```

Then visit:
- http://localhost:8000/ - Welcome message
- http://localhost:8000/agents/ - List all agents
- http://localhost:8000/agents/chat/assistant - Get the assistant agent
- http://localhost:8000/agents/tasks/reminder - Get the reminder agent 