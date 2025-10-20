### File: osb_agent_app/goal_generator_llm.py

import os
from typing import List, Dict
from .gemini_client import initialize_gemini_client
import markdown
from bs4 import BeautifulSoup
from .planner_rules import get_task_dependencies
from config import GOOGLE_API_KEY, GEMINI_MODEL2

# List of supported high-level goals with descriptions
AVAILABLE_TASKS = [
    {"name": "get_studies", "description": "look for the existent studies, to check uniqueness"},
    {"name": "create_study", "description": "Perform the task of creating 1 'create_study'."},
    {"name": "create_study_arm", "description": "Perform the task of creating 1 'create_study_arm'."},
    {"name": "create_epoch", "description": "Perform the task of creating 1 'create_epoch'."},
    {"name": "preview_epoch", "description": "fills the needed data to perform the creation of the epoch Perform the task preview 1 'preview_epoch'."},
    {"name": "create_element", "description": "Perform the task of creating 1 'create_element'."},
    {"name": "fetch_arm_control_terminology", "description": "Perform the task 'fetch_arm_control_terminology'."},
    {"name": "fetch_epoch_control_terminology", "description": "Perform the task 'fetch_epoch_control_terminology'."},
    {"name": "fetch_element_control_terminology", "description": "Perform the task 'fetch_element_control_terminology'."},
    {"name": "fetch_activity_type_terminology", "description": "Retrieves control terminology for activity type."},
    {"name": "fetch_soa_group_control_terminology", "description": "Retrieves control terminology for activity schedule of activities groups."},
    {"name": "create_study_activity", "description": "Defines study activities."},
    {"name": "get_study_activity", "description": "get study activities to check uniqueness."},

    {"name": "create_activity_schedule", "description": "Defines create visit activity schedule"},
    {"name": "get_activity_schedule", "description": "gets visit activity schedule"},
    {"name": "create_design_cell", "description": "Defines create design cell"},

    {"name": "create_visit", "description": "Perform the task of creating 1 'create_visit'."},
    {"name": "preview_visit", "description": "fills the needed data to perform the creation of the visit Perform the task preview 1 'preview_visit'."},
    {"name": "fetch_time_point_reference_control_terminology", "description": "Perform the task 'fetch_time_point_reference_control_terminology'."},
    {"name": "fetch_visit_control_terminology", "description": "Perform the task 'fetch_visit_control_terminology'."},
    {"name": "get_study_visits", "description": "get study visits to check uniqueness in timeline."},
    {"name": "get_activity_schedule", "description": "get study visits activity schedules to check uniqueness in timeline."},
    {"name": "get_study_epochs", "description": "get study epochs to check uniqueness."},
    {"name": "get_study_arms", "description": "get study arms to check uniqueness."},
]



def extract_code_from_markdown(markdown_text: str) -> str:
    html = markdown.markdown(markdown_text, extensions=["fenced_code"])
    soup = BeautifulSoup(html, "html.parser")
    code_block = soup.find("code")
    return code_block.text.strip() if code_block else markdown_text.strip()

class GoalGeneratorLLM:
    """
    Wrapper around a language model (Gemini) to map a free-form user request
    into an ordered list of high-level goal names, constrained to AVAILABLE_TASKS.
    """
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = 0,
    ):
        dict(os.environ)
        # Initialize Gemini client
        self.client = initialize_gemini_client(
            api_key=GOOGLE_API_KEY,
            model=GEMINI_MODEL2
        )
        print("printing all teh keys of envrionment ")
        print(os.getenv("GEMINI_API_KEY"),os.getenv("GEMINI_MODEL", "gemini-pro") )
        self.temperature = temperature

    def generate_goals(self, user_request: str) -> List[str]:
        """
        Generate an ordered list of goal names based on a free-form user request.

        Args:
            user_request (str): The user's natural language request.

        Returns:
            List[str]: Ordered list of goal names matching AVAILABLE_TASKS. Each task creates one item, list multiple times if there's the need of creating many. 
        """
        # Build the prompt including task list
        task_lines = "".join([
            f"- {t['name']}: {t['description']}\n"
            for t in AVAILABLE_TASKS
        ])
        prompt = (
            "You are an assistant that maps user requests into orchestrator tasks, if the user ask for multiple items repeat the task. "
            "Here are the supported tasks, if multiple items of the same to be create repeat the task:"
            f"{task_lines}"
            f"User request: \"{user_request}\""
            "Return a Python list of taks names in execution order. No extra text. Each task creates one item, list multiple times if there's the need of creating many. "
        )

        # Call Gemini
        response = self.client.generate_content(prompt
        )
        # Parse the response content
        content = extract_code_from_markdown(response.text.strip())
        # Safely evaluate the returned Python list
        try:
            goals = eval(content)
        except Exception:
            raise ValueError(f"Unable to parse goals list: {content}")
        return goals

# goal_generator_llm.py

def generate_task_plan(context):
    task_plan = []
    task_name = "study_arm"
    dependencies = get_task_dependencies(task_name, context)
    task_plan.extend(dependencies)
    task_plan.append(task_name)
    return task_plan
