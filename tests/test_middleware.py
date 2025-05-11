import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pathlib import Path
from agent_middleware import AgentMiddleware

@pytest.fixture
def app():
    app = FastAPI()
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

@pytest.fixture
def agents_dir(tmp_path):
    # Create a temporary agents directory
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    
    # Create a sample agent
    chat_dir = agents_dir / "chat"
    chat_dir.mkdir()
    
    agent_data = {
        "name": "Test Agent",
        "description": "A test agent",
        "version": "1.0.0"
    }
    
    with open(chat_dir / "assistant.json", "w") as f:
        json.dump(agent_data, f)
    
    return agents_dir

def test_middleware_initialization(app, agents_dir):
    middleware = AgentMiddleware(app, agents_dir=str(agents_dir))
    assert middleware.agents_dir == agents_dir
    assert middleware.base_path == "/agents"
    assert not middleware.auto_reload

def test_list_agents(client, app, agents_dir):
    AgentMiddleware(app, agents_dir=str(agents_dir))
    response = client.get("/agents/")
    assert response.status_code == 200
    assert "agents" in response.json()
    assert "chat/assistant" in response.json()["agents"]

def test_get_agent(client, app, agents_dir):
    AgentMiddleware(app, agents_dir=str(agents_dir))
    response = client.get("/agents/chat/assistant")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Agent"
    assert response.json()["version"] == "1.0.0"

def test_agent_not_found(client, app, agents_dir):
    AgentMiddleware(app, agents_dir=str(agents_dir))
    response = client.get("/agents/nonexistent")
    assert response.status_code == 404

def test_before_hook(client, app, agents_dir):
    middleware = AgentMiddleware(app, agents_dir=str(agents_dir))
    
    hook_called = False
    def before_hook(request, agent_path):
        nonlocal hook_called
        hook_called = True
    
    middleware.add_before_hook("chat/*", before_hook)
    response = client.get("/agents/chat/assistant")
    assert response.status_code == 200
    assert hook_called

def test_after_hook(client, app, agents_dir):
    middleware = AgentMiddleware(app, agents_dir=str(agents_dir))
    
    hook_called = False
    def after_hook(request, response, agent_path, agent_data):
        nonlocal hook_called
        hook_called = True
    
    middleware.add_after_hook("chat/*", after_hook)
    response = client.get("/agents/chat/assistant")
    assert response.status_code == 200
    assert hook_called 