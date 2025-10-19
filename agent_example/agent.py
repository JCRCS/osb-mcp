#%%

from agent_example.planner.logic import generate_goals, generate_list
from agent_example.planner.rules import AVAILABLE_TASKS, SUB_AGENT_MAP
import nest_asyncio
nest_asyncio.apply()
import asyncio
import os
import logging
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from config import (
    GEMINI_MODEL,
    NOVO_API,
    NOVO_TOKEN,
    NOVO_MODEL,
)
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.sessions import InMemorySessionService  # MODIFIED IMPORT PATH
from google.ai.generativelanguage_v1beta.types import Content, Part
import traceback
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
import logging
from collections import defaultdict
import nest_asyncio
from pyparsing import Dict
from rpds import List



def group_tasks_by_agent(tasks):
    """
    Groups tasks by their assigned agent.
    Returns a dict: {agent_name: [task, ...]}
    """
    agent_tasks = defaultdict(list)
    for task in tasks:
        agent_tasks[task['agent']].append(task)
    return agent_tasks

async def instantiate_agents(model, instruction, available_tasks=AVAILABLE_TASKS):
    """
    Instantiates LlmAgent objects for each agent, assigning their respective tasks and toolsets.
    Returns a dict: {agent_name: LlmAgent}
    """
    agent_tasks = group_tasks_by_agent(available_tasks)
    agents = {}
    for agent_name, tasks in agent_tasks.items():
        description = "\n".join(f"- {task['description']}" for task in tasks)
        tools_list = [task['name'] for task in tasks]
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "./main.py"],
        )
        osb_mcp_toolset = MCPToolset(connection_params=server_params, tool_filter=tools_list)
        agent = LlmAgent(
            model=model,
            name=agent_name,
            instruction=instruction,
            tools=[osb_mcp_toolset],
            description=description,
        )
        agents[agent_name] = agent
    return agents

def create_coordinator_agent(name, model, description, instruction, sub_agent_names, agent_instances):
    """
    Creates a coordinator LlmAgent with the specified sub-agents.
    """
    return LlmAgent(
        model=model,
        name=name,
        description=description,
        instruction=instruction,
        sub_agents=[agent_instances[agent_name] for agent_name in sub_agent_names]
    )

def create_root_agent(model, product_outline_agent, schedule_of_activities_agent, planner_instruction):
    """
    Creates the root planner agent with its coordinator sub-agents.
    """
    return LlmAgent(
        model=model,
        name="RootPlannerAgent",
        description="The master orchestrator for the Clinical Trial Automation system. I create plans and delegate them to my coordinators.",
        instruction=planner_instruction,
        sub_agents=[
            product_outline_agent,
            schedule_of_activities_agent,
        ],
        tools=[generate_goals, generate_list]
    )

# Load environment variables
load_dotenv()
os.environ["OTEL_PYTHON_CONTEXT"] = "asyncio"
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


GENERAL_INSTRUCTION = (
    "Forget ALL Previously stated, you'll receive your goal and the functions you are capable to perform"
    "You are the Open Study Builder Agent (open_study_builder_agent). Execute only the assigned tasks from the root_agent do not plan or infer. if the user gives you an instruction TRANSFER it to the planner\n"
    "- If inputs are missing or invalid, return an error.\n"
    "- Respect the order that the root_agent states on the passed plan. If a task gives an error TRANSFER it to the root_agent\n"
    "- If a task cannot be executed, respond with a clear failure message for the root_agent.\n"
    "== ERROR HANDLING & ESCALATION ==\n"
    "- If a task cannot be completed due to missing context, misalignment, or an unexpected error, TRANSFER a structured error message to the root_agent Agent. DON'T CONTINUE\n"
    "- Do not attempt to ask the user or resolve ambiguity—rely on the root_agent to handle that.\n\n"
    "== FINAL STAGE ==\n"
    "- always when finish the tasks TRANSFER to root_agent agent with a summary\n"
    "- when you've finished passing all the planned tasks give a summary of the activities you've done to the root_agent agent, if it's a get task TRANSFER the result to the root_agent agent\n"
)

PLANNER_INSTRUCTION = """
== ROLE & GOAL ==
You are the RootPlannerAgent, a master orchestrator for a complex Clinical Trial Protocol (MCP) API. Your sole purpose is to receive a high-level user goal (e.g., 'Create a new oncology study with two arms, a screening phase, and a treatment phase') and decompose it into a precise, executable, step-by-step plan. You DO NOT execute tasks yourself; you create plans for your sub-agents to execute.

== PRIMARY DIRECTIVE: STATE-AWARE, DEPENDENCY-DRIVEN PLANNING ==
Your operation is governed by two critical components: the Task Dependency Matrix and the Session State.

1.  **Task Dependency Matrix**: This is your absolute source of truth for API logic. Before generating any plan, you MUST perform a chain-of-thought analysis referencing this matrix to identify all prerequisite tasks.
2.  **Session State (session.state)**: This is the shared memory of the agent system. Your plans MUST be state-aware. When a task retrieves data (e.g., get_studies), your plan must include a step to store this data in session.state. When a task requires data, your plan must specify the session.state key from which to retrieve it.

== PLANNING PROCESS (MANDATORY CHAIN-OF-THOUGHT) ==
For every user request, you must follow this internal monologue:
1.  **Deconstruct Goal**: Break down the user's request into the core entities that need to be created (e.g., Study, Arm, Epoch).
2.  **Consult Matrix**: For each entity, look up its creation task in the Task Dependency Matrix. Systematically list all its prerequisite tasks.
3.  **Resolve Dependencies**: Construct a directed acyclic graph (DAG) of all required tasks, ensuring prerequisites execute before the tasks that depend on them.
4.  **Inject State Management**: For each dependency, explicitly define the data handoff.
5.  **Assign Agents**: Using the agent descriptions, assign the correct specialist or coordinator agent to each task.
6.  **Generate Plan**: Output the final, ordered list of tasks as a JSON object according to the specified format.

== OUTPUT FORMAT: MACHINE-READABLE PLAN ==
Your final output MUST be a single JSON object containing a key "plan" which is an array of task objects. Do not output any other text or explanation. Each task object must have this structure:
{
  "task_name": "name_of_the_task_to_execute",
  "agent_name": "name_of_the_agent_responsible",
  "description": "A brief description of this step's purpose.",
  "inputs": { "parameter_name_1": "session.state.key_for_input_1" },
  "outputs": { "result_name_1": "session.state.key_to_store_output_1" }
}

== ERROR HANDLING & REPLANNING ==
If a sub-agent reports a failure, analyze the error and the state, then either replan or ask the user for clarification.

== TASK DEPENDENCY MATRIX ==
- create_study: requires get_studies
- create_study_arm: requires create_study (for study_id), fetch_arm_control_terminology
- (and so on for all other dependencies)
"""


# --- Instantiate Agents ---
# This part is often run at the module level if the ADK CLI expects `root_agent` to be globally defined.
# The asyncio.run() call is for scripts that need to initialize async components synchronously at startup.

# Initialize instance variables outside the try block to ensure they exist in all paths
open_study_builder_agent_instances = None

# Create Google Search Agent and its exit stack
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        print("Asyncio loop already running. Creating agents within the current loop.")
        # Google Search_agent, Google Search_exit_stack = loop.run_until_complete(create_Google Search_agent()) # Potential error source
        print("Creating OpenStudyBuilder agent (placeholder)...")  # This line prints
        open_study_builder_agent_instances = loop.run_until_complete(
            instantiate_agents(GEMINI_MODEL,GENERAL_INSTRUCTION)
            # create_open_study_builder_agent()
        )  # Potential error source
    else:
        # Google Search_agent, Google Search_exit_stack = asyncio.run(create_Google Search_agent()) # Potential error source
        print("Creating OpenStudyBuilder agent (placeholder)...")
        open_study_builder_agent_instances = asyncio.run(
            instantiate_agents(GEMINI_MODEL,GENERAL_INSTRUCTION)
            # create_open_study_builder_agent()
        )
except Exception as e:
    print(f"CRITICAL ERROR DURING AGENT INSTANTIATION AT IMPORT TIME: {e}")
    traceback.print_exc()

    print("Attempting to create dummy agents as fallbacks...")
    # Define dummy for open_study_builder_agent if it failed (or if any failed)
    if (
        open_study_builder_agent_instances is None
    ):  # Check if it wasn't successfully created
        open_study_builder_agent_instances = {
            "dummy_open_study_builder_agent_on_error": LlmAgent(
                name="dummy_open_study_builder_agent_on_error",
                instruction="This is a dummy OpenStudyBuilder agent. The real one failed to initialize.",
                model=LiteLlm(
                    model=NOVO_MODEL,
                    api_base=NOVO_API,
                    api_key=NOVO_TOKEN,
                    # description="This is a dummy OpenStudyBuilder agent",
                ),
            )
        }
        print("Created dummy OpenStudyBuilder agent.")

# --- Level 1: Domain Coordinator Agents ---
product_outline_agent = create_coordinator_agent(
    name="ProductOutlineAgent",
    model=LiteLlm(
        model=NOVO_MODEL,
        api_base=NOVO_API,
        api_key=NOVO_TOKEN,
        # description="Coordinator agent for OpenStudyBuilder agent",
        tools=[], # Root agent might have its own tools or just coordinate
    ),
    description="A specialized coordinator responsible for managing the creation of a clinical study's product outline, including arms, epochs, visits, and elements. I receive a sub-plan and delegate tasks to my team of specialist agents.",
    instruction="You are a sub-project manager. You will receive an ordered list of tasks in a JSON plan. Delegate each task, one by one and in the exact order specified, to the correct specialist agent in your `sub_agents` list. Use the `agent_name` from the task object to delegate. If any task fails, halt immediately and TRANSFER the failure to the `RootPlannerAgent`.",
    sub_agent_names=SUB_AGENT_MAP["Product_out_line_sub_agent"],
    agent_instances=open_study_builder_agent_instances
)

schedule_of_activities_agent = create_coordinator_agent(
    name="ScheduleOfActivitiesAgent",
    model=LiteLlm(
        model=NOVO_MODEL,
        api_base=NOVO_API,
        api_key=NOVO_TOKEN,
        # description="Coordinator agent for OpenStudyBuilder agent",
        tools=[], # Root agent might have its own tools or just coordinate
    ),
    description="A specialized coordinator responsible for managing the creation of a study's schedule of activities. I receive a sub-plan and delegate tasks to my specialist agents.",
    instruction="You are a sub-project manager. You will receive an ordered list of tasks in a JSON plan. Delegate each task, one by one and in the exact order specified, to the correct specialist agent in your `sub_agents` list. Use the `agent_name` from the task object to delegate. If any task fails, halt immediately and TRANSFER the failure to the `RootPlannerAgent`.",
    sub_agent_names=SUB_AGENT_MAP["Schedule_of_Activitites_sub_agent"],
    agent_instances=open_study_builder_agent_instances
)

root_agent = create_root_agent(
    model=LiteLlm(
        model=NOVO_MODEL,
        api_base=NOVO_API,
        api_key=NOVO_TOKEN,
        # description="Coordinator agent for OpenStudyBuilder agent",
        tools=[], # Root agent might have its own tools or just coordinate
    ),
    product_outline_agent=product_outline_agent,
    schedule_of_activities_agent=schedule_of_activities_agent,
    planner_instruction=PLANNER_INSTRUCTION
)

# --- Set Up Runner and Session (for local testing or custom execution) ---
session_service = InMemorySessionService()

if __name__ == "__main__":
    print("Multi-Agent App. Type 'exit' to quit.")

    app_name_for_session = "multi_agent_app"
    session_id = "session_" + os.urandom(4).hex()
    user_id = "user_" + os.urandom(4).hex()

    runner = Runner(
        app_name=app_name_for_session,
        agent=root_agent,
        session_service=session_service,
    )

    try:
        while True:
            user_input = input("User: ")
            if user_input.strip().lower() in ("exit", "quit"):
                break

            # Use the directly imported Content and Part
            message_content = Content(  # Renamed variable to avoid conflict if 'content' is used elsewhere
                role="user",
                parts=[Part(text=user_input)],  # Use the directly imported Part
            )

            print(
                f"\nAssistant (processing for session: {session_id}, user: {user_id}, app: {app_name_for_session}):"
            )

            events = runner.run(
                session_id=session_id,
                user_id=user_id,
                new_message=message_content,  # Pass the correctly typed message_content
            )

            full_response_text = ""
            for evt in events:
                if evt.message_content and evt.message_content.text:
                    full_response_text += evt.message_content.text
                elif evt.content_chunk and evt.content_chunk.text:
                    full_response_text += evt.content_chunk.text
                print(f"DEBUG Event: {evt.event_type}, Data: {evt}")

            print(full_response_text)

    finally:
        print("\nShutting down MCP connections and other resources...")
        print("Shutdown complete.")

# %%
