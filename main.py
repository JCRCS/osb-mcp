# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# Import the OSB agent entrypoint and descriptor
from osb_agent_app.agent import run_llm_driven_workflow
from osb_agent_app.agent_descriptor import AGENT_DESCRIPTOR

app = FastAPI(title="Open Study Builder MCP")

# Agent registry: maps agent key → handler function and descriptor
AGENT_HANDLERS = {
    AGENT_DESCRIPTOR["agent_name"]: {
        "run": run_llm_driven_workflow,
        "descriptor": AGENT_DESCRIPTOR
    }
}


class MCPRequest(BaseModel):
    agent: str
    user_input: str


class MCPResponse(BaseModel):
    status: str
    results: Any


@app.get("/mcp/agents/{agent}", response_model=Dict[str, Any])
async def get_agent_descriptor(agent: str):
    """
    Returns metadata about the specified agent, including available tools.
    """
    entry = AGENT_HANDLERS.get(agent)
    if not entry:
        raise HTTPException(status_code=404, detail="Agent not found")
    return entry["descriptor"]


@app.post("/mcp/run", response_model=MCPResponse)
async def mcp_run(req: MCPRequest):
    """
    Invokes the specified agent with the user_input.
    Returns the step-by-step execution results.
    """
    entry = AGENT_HANDLERS.get(req.agent)
    if not entry:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Execute the agent’s workflow
    results = entry["run"](req.user_input)
    return MCPResponse(status="ok", results=results)
