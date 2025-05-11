from fastapi import FastAPI, Request, Response
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from agent_middleware import AgentMiddleware
from agent_middleware.logging_config import setup_logging
import time
import logging

# Set up colored logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent Middleware Example",
    description="A FastAPI application demonstrating the Agent Middleware with AutoGen integration",
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
)

# Initialize the agent middleware with OpenAI configuration
agent_middleware = AgentMiddleware(
    app=app,
    agents_dir="agents",
    base_path="/agents",
    auto_reload=True,  # Set to True to reload agents on each request
    config_list=[
       # {
       #     "model": "gpt-3.5-turbo",
      #      "api_key": "your-openai-api-key"  # Replace with your actual API key
        #}
    ]
)

# Example before hook - Log access and add timing
def log_access(request: Request, agent_path: str):
    logger.info(f"Accessing agent: {agent_path} from {request.client.host}")

# Example before hook - Add request timing
def add_timing(request: Request, agent_path: str):
    request.state.start_time = time.time()

# Example after hook - Log response time
def log_response_time(request: Request, response: Response, agent_path: str, agent_data: dict):
    if hasattr(request.state, 'start_time'):
        duration = time.time() - request.state.start_time
        logger.info(f"Request to {agent_path} took {duration:.2f} seconds")

# Example after hook - Modify response
def add_metadata(request: Request, response: Response, agent_path: str, agent_data: dict):
    if isinstance(agent_data, dict):
        agent_data['_metadata'] = {
            'accessed_at': time.time(),
            'client_ip': request.client.host
        }

# Add hooks to specific agents
agent_middleware.add_before_hook("chat/*", log_access)  # Apply to all chat agents
agent_middleware.add_before_hook("*", add_timing)  # Apply to all agents
agent_middleware.add_after_hook("*", log_response_time)  # Apply to all agents
agent_middleware.add_after_hook("tasks/*", add_metadata)  # Apply to all task agents

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Agent Middleware Example",
        "endpoints": {
            "list_agents": "/agents/",
            "get_agent": "/agents/{agent_path}",
            "chat_with_agent": "/agents/{agent_path}/chat"
        },
        "documentation": "/docs"
    }

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Agent Middleware API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint():
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 