### File: osb_agent_app/goal_generator_llm.py

import os
from typing import List, Dict
from .gemini_client import initialize_gemini_client
import markdown
from bs4 import BeautifulSoup

# List of supported high-level goals with descriptions
AVAILABLE_TASKS = [
    {"name": k, "description": f"Perform the goal '{k}'."}
    for k in [
        "create_study",
        "create_study_arms",
        "create_epochs",
        "create_branch_arms",
        "create_elements",
        "fetch_arm_control_terminology",
        "fetch_epoch_control_terminology",
        "fetch_branch_arm_control_terminology",
        "fetch_element_control_terminology",
    ]
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
            api_key=api_key or os.getenv("GEMINI_API_KEY"),
            model=model or os.getenv("GEMINI_MODEL", "gemini-pro")
        )
        self.temperature = temperature

    def generate_goals(self, user_request: str) -> List[str]:
        """
        Generate an ordered list of goal names based on a free-form user request.

        Args:
            user_request (str): The user's natural language request.

        Returns:
            List[str]: Ordered list of goal names matching AVAILABLE_TASKS.
        """
        # Build the prompt including task list
        task_lines = "".join([
            f"- {t['name']}: {t['description']}" for t in AVAILABLE_TASKS
        ])
        prompt = (
            "You are an assistant that maps user requests into orchestrator goals. "
            "Here are the supported goals:"
            f"{task_lines}"
            f"User request: \"{user_request}\""
            "Return a Python list of goal names in execution order. No extra text."
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

