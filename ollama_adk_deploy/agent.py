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

ollama_model_gemini=os.getenv("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25")

from pydantic import Field, PrivateAttr
from google.adk.models import BaseLlm
from typing import Any, Dict

class LiteLlmWrapper(BaseLlm):
    model: str = Field(..., description="The model name")
    litellm_params: Dict[str, Any] = Field(..., description="Additional parameters to configure the LLM")

    # Define private attribute
    _lite_llm = PrivateAttr()

    def __init__(self, lite_llm, litellm_params: Dict[str, Any] = None):
        super().__init__(model=lite_llm.model)
        self._lite_llm = lite_llm
        self.litellm_params = litellm_params or {}

    async def __aiter__(self):
        """Initialize the asynchronous iterator."""
        # Optionally, store initial state, such as the request or configuration
        self._llm_request = None  # Or set this based on your configuration
        return self

    async def __anext__(self):
        """Return the next item for the asynchronous iteration."""
        if self._llm_request is None:
            # Initialize the request on the first call to __anext__()
            self._llm_request = {"messages": [{"role": "user", "content": "Your request here"}]}  # Example request

        # Use the generate_content_async method to get content, possibly streaming in chunks
        async for content in self.generate_content_async(self._llm_request['messages']):
            return content

    async def generate_content_async(self, messages, tools=None, **kwargs):
        """Async method to generate content, yielding multiple responses (as an iterable)."""
        
        # Determine the provider (e.g., OpenAI)
        provider = self.litellm_params.get("messages_provider", "openai")
        
        completion_kwargs = {}
        if tools:
            completion_kwargs["tools"] = tools
        completion_kwargs.update(kwargs)
        
        # Based on provider, adjust how messages are handled (e.g., OpenAI vs other services)
        if provider == "openai":
            response = await self._lite_llm.acompletion(messages=messages, **completion_kwargs)
        else:
            # Handle other providers here (if applicable)
            response = await self._lite_llm.acompletion(messages=messages, **completion_kwargs)
        
        # Check if there are multiple choices (e.g., for streaming purposes)
        choices = response.get("choices", [])
        if choices:
            for choice in choices:
                content = choice["message"]["content"]
                if content:
                    yield content  # Yield the content to make this an iterable

        # If no content found, raise StopAsyncIteration (or return if needed)
        raise StopAsyncIteration

ollama_model = LiteLlm(model="ollama/llama3.2:1B", litellm_params={"messages_provider": "openai"} )



# # --- Step 1b: Initialize Open Study Builder MCP Agent ---
async def create_open_study_builder_agent():
    """Fetches MCP tools and returns an LlmAgent for OpenStudyBuilder API."""
    server_params = StdioServerParameters(
        command="uv",
        args=["run" ,"./main.py"],
    )
    tools, osb_exit_stack = await MCPToolset.from_server(connection_params=server_params)
    osb_agent = LlmAgent(
        # model=,
        model = ollama_model_gemini,
        name="root_agent",
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
    "Only call functions explicitly provided. Never invent or guess function names."
    "- If unable to handle, respond that you cannot handle the request."
)


#... (rest of file unchanged, except include new agent in root)

root_agent = Agent(
    name="root_agent",
    model="llama3.2:1B",
    instruction=root_instruction,
    description="Coordinator agent for greetings, weather, farewells, flight search, and OpenStudyBuilder.",
    tools=[],#get_weather],
    sub_agents=[open_study_builder_agent]#greeting_agent, farewell_agent, 
                # flight_search_agent, 
                #open_study_builder_agent]
)
# server_params = StdioServerParameters(
#     command="uv",
#     args=["run" ,"./../../ennio-2/MCP_Server/src/my_mcp_server/__main__.py"],
# )
# tools, osb_exit_stack = MCPToolset.from_server(connection_params=server_params)
# root_agent = LlmAgent(
#     # model=,
#     model="ollama/llama3.2:1B",
#     name="root_agent",
#     instruction=(
#         "Help the user interact with the OpenStudyBuilder API via the available tools."
#     ),
#     tools=tools,
# )

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
