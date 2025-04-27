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
from google.genai import types

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm



# Load environment variables
load_dotenv()
import os
os.environ["OTEL_PYTHON_CONTEXT"] = "asyncio"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ollama_model1 = LiteLlm(model="ollama/llama3.1:8b")
# ollama_model2 = LiteLlm(model="ollama/llama3.1:latest")
# ollama_model3 = LiteLlm(model="ollama/llama3.2:3b", litellm_params={"messages_provider": "openai"} )
# ollama_model4 = LiteLlm(model="ollama/llama3.2:1B", litellm_params={"messages_provider": "openai"} )
ollama_model4=os.getenv("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25")
ollama_model3="gemini-2.0-flash-exp"
# # --- Step 1: Initialize Flight Search MCP Agent ---
# async def create_flight_search_agent():
#     """Fetches MCP tools and returns an LlmAgent for flight search."""
#     server_params = StdioServerParameters(
#         command="mcp-flight-search",
#         args=["--connection_type", "stdio"],
#         env={"SERP_API_KEY": os.getenv("SERP_API_KEY")},
#     )
#     tools, flight_exit_stack = await MCPToolset.from_server(connection_params=server_params)
#     flight_agent = LlmAgent(
#         model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25"),
#         name="flight_search_agent",
#         instruction=(
#             "Help the user search for flights using the available tools. "
#             "If no return date is specified, treat it as a one-way trip."
#         ),
#         tools=tools,
#     )
#     return flight_agent, flight_exit_stack 

# --- Step 1b: Initialize Open Study Builder MCP Agent ---
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
            "Help the user interact with the OpenStudyBuilder API via the available tools."
        ),
        tools=tools,
    )
    return osb_agent, osb_exit_stack

open_study_builder_agent, osb_exit_stack = asyncio.run(create_open_study_builder_agent())

# --- Step 2: Define Local Tool Functions and Agents ---
def say_hello(name: str = "there") -> str:
    print(f"--- Tool: say_hello called with name: {name} ---")
    return f"Hello, {name}!"

def say_goodbye() -> str:
    print("--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

def get_weather(city: str) -> dict:
    if city.lower() == "new york":
        return {"status": "success", "report": "The weather in New York is sunny at 25°C."}
    return {"status": "error", "error_message": f"Weather for '{city}' not available."}

# # Greeting Agent
# greeting_agent = Agent(
#     name="greeting_agent",
#     model = ollama_model4,
#     instruction="You are the Greeting Agent. Use say_hello tool to greet.",
#     description="Provides greetings.",
#     tools=[say_hello]
# )

# # Farewell Agent
# farewell_agent = Agent(
#     name="farewell_agent",
#     model = ollama_model4,
#     instruction="You are the Farewell Agent. Use say_goodbye tool to say goodbye.",
#     description="Provides farewells.",
#     tools=[say_goodbye]
# )

# --- Step 3: Define Root Agent with Delegation Rules ---
root_instruction = (
    "You are the Root Agent orchestrating sub-agents. "
    "- Delegate studies related queries to osb_agent"
    "- If unable to handle, respond that you cannot handle the request."
)


#... (rest of file unchanged, except include new agent in root)

root_agent = Agent(
    name="root_agent",
    model=ollama_model4,
    instruction=root_instruction,
    description="Coordinator agent for greetings, weather, farewells, flight search, and OpenStudyBuilder.",
    tools=[],#get_weather],
    sub_agents=[open_study_builder_agent]#greeting_agent, farewell_agent, 
                # flight_search_agent, 
                #open_study_builder_agent]
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
    print("Multi-Agent Flight Search & Study Builder App Type 'exit' to quit.")
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
        # asyncio.run(flight_exit_stack.aclose())
        asyncio.run(osb_exit_stack.aclose())
        print("Shutdown complete.")
