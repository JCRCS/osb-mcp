from agent_example.planner.rules import (
    PLANNER_RULES,
    TASK_DEPENDENCIES,
    AVAILABLE_TASKS,
)
import nest_asyncio
nest_asyncio.apply()
import logging
import markdown
from bs4 import BeautifulSoup
import logging


def extract_code_from_markdown(markdown_text: str) -> str:
    html = markdown.markdown(markdown_text, extensions=["fenced_code"])
    soup = BeautifulSoup(html, "html.parser")
    code_block = soup.find("code")
    return code_block.text.strip() if code_block else markdown_text.strip()


def generate_goals(user_request: str) -> str:
    """
    Generate an ordered list of goal names based on a free-form user request.

    Args:
        user_request (str): The user's natural language request.

    Returns:
        List[str]: Ordered list of goal names matching AVAILABLE_TASKS. Each task creates one item, list multiple times if there's the need of creating many.
    """
    logging.info(f"INSIDE GENERATE GOALS, USER REQUEST IS: {user_request}")
    # Build the prompt including task list
    task_lines = "".join(
        [f"- {t['name']}: {t['description']}\n" for t in AVAILABLE_TASKS]
    )
    prompt: str = (
        "Here are the supported tasks, if multiple items of the same to be create repeat the task:"
        f"{task_lines}"
        f'User request: "{user_request}"'
        "Send to generate_list a Python list of taks names in execution order. "
        "For example ['create_study'] or ['create_study','create_arm']"
        "No extra text. Each task creates one item, list multiple times if there's the need of creating many. "
    )

    # Call Gemini
    return prompt


# Build a mapping from task name to agent for quick lookup
TASK_AGENT_MAP = {t["name"]: t.get("agent") for t in AVAILABLE_TASKS}

def get_agent_for_task(task_name: str) -> str:
    """
    Returns the agent assigned to the given task name.
    """
    return TASK_AGENT_MAP.get(task_name)


def plan_method(goals: list[str]) -> list[dict]:
    ordered_goals: list[str] = []
    visited = set()

    def visit(g: str):
        if g in visited:
            return
        for dep in TASK_DEPENDENCIES.get(g, []):
            visit(dep)
        if g not in ordered_goals:
            ordered_goals.append(g)
        visited.add(g)

    for g in goals:
        if g not in PLANNER_RULES:
            raise ValueError(f"No rule defined for goal: {g}")
        visit(g)

    # Expand each goal into its atomic tasks, now as dicts with agent info
    tasks: list[dict] = []
    for g in ordered_goals:
        for task_name in PLANNER_RULES[g]:
            agent = get_agent_for_task(task_name)
            tasks.append({"name": task_name, "agent": agent})
    return tasks


def generate_list(text_response: str):
    # Parse the response content
    content = extract_code_from_markdown(text_response.strip())
    # Safely evaluate the returned Python list
    try:
        tasks = eval(content)
    except Exception:
        raise ValueError(f"Unable to parse goals list: {content}")
    plan = plan_method(goals=tasks)
    return plan
