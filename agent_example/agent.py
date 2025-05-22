import nest_asyncio
nest_asyncio.apply()

import asyncio
import os
import logging
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.generativeai import types

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import google_search
# from google.adk.models import GoogleGeminiModel




# Load environment variables
load_dotenv()
import os
os.environ["OTEL_PYTHON_CONTEXT"] = "asyncio"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ollama_model4=os.getenv("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25")
ollama_model3="gemini-2.0-flash-exp" #""

import os
import asyncio
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

async def create_google_search_agent():
    tools, exit_stack = await MCPToolset.from_server(
    connection_params=StdioServerParameters(
        command="uv",
        args=["run" ,"./mcp_google_search_server.py"],
    ))
    google_search_agent = LlmAgent(model="gemini-2.5-pro-preview-03-25",
                     name="google_search_agent",
                     tools=tools)
    return google_search_agent, exit_stack
google_search_agent, google_search_exit_stack = asyncio.run(create_google_search_agent())


async def create_open_study_builder_agent():
    """Fetches MCP tools and returns an LlmAgent for OpenStudyBuilder API."""
    server_params = StdioServerParameters(
        command="uv",
        args=["run" ,"./main.py"],
    )
    tools, osb_exit_stack = await MCPToolset.from_server(connection_params=server_params)
    osb_agent = LlmAgent(
        # model=,
        model = ollama_model3,
        name="open_study_builder_agent",
        instruction=(
            "Help the user interact with the OpenStudyBuilder API via the available tools. First call the planner and the use the tools"
        ),
        tools=tools,
    )
    return osb_agent, osb_exit_stack

open_study_builder_agent, osb_exit_stack = asyncio.run(create_open_study_builder_agent())

# --- Define Root Agent with Delegation Rules ---
root_instruction = (
    "You are the Root Agent orchestrating sub-agents. "
    "- Delegate studies related queries to osb_agent"
    "- Delegate google search related queries to google_search_agent"
    "- If unable to handle, respond that you cannot handle the request."
)



root_agent = Agent(
    name="root_agent",
    model=ollama_model3,
    instruction=root_instruction,
    description="Coordinator agent for OpenStudyBuilder agent and google search agent.",
    tools=[],
    sub_agents=[open_study_builder_agent, google_search_agent]
)

# --- Step 4: Set Up Runner and Session ---
session_service = InMemorySessionService()
session = session_service.create_session(state={}, app_name="multi_agent_app", user_id="user_1")

runner = Runner(
    app_name="multi_agent_app",
    agent=root_agent,
    session_service=session_service
)

# --- Step 5: Main Loop ---
if __name__ == "__main__":
    print("Study Builder App Type 'exit' to quit.")
    try:
        while True:
            user_input = input("User: ")
            if user_input.strip().lower() in ("exit", "quit"):
                break
            content = types.Content(role='user', parts=[types.Part(text=user_input)])
            events = runner.run(session_id=session.id, user_id=session.user_id, new_message=content)
            for evt in events:
                print(evt)
    finally:
        print("Shutting down MCP connections...")
        asyncio.run(osb_exit_stack.aclose())
        asyncio.run(google_search_exit_stack.aclose())
        print("Shutdown complete.")
