# osb_agent_app/goal_generator_llm.py

import os
from typing import List


# List of supported high-level goals
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

class GoalGeneratorLLM:
    """
    Uses GPT-4 to map a free-form user request into an ordered list of
    high-level goal names, constrained to AVAILABLE_TASKS.
    """
    def __init__(self, model: str = "gpt-4"):
        self.model = model

    def generate_goals(self, user_request: str) -> List[str]:
        task_list = "\n".join([f"- {t['name']}: {t['description']}" for t in AVAILABLE_TASKS])
        prompt = f"""
You are an assistant that maps user requests into orchestrator goals.

Here are the supported goals:
{task_list}

User request: "{user_request}"

Return a Python list of goal names in execution order. No extra text.
"""
        resp = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        # The model should return something like: ["create_study", "create_study_arms", ...]
        goals = eval(resp.choices[0].message["content"].strip())
        return goals
