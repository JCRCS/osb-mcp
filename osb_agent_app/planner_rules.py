# osb_agent_app/planner_rules.py

"""
Defines high-level goal → atomic-task sequences and inter-goal dependencies.
"""

# Map each high-level goal to its list of atomic tasks.
PLANNER_RULES = {
    "create_study": ["create_study"],
    "create_study_arms": ["create_study_arms"],
    "create_epochs": ["create_epochs"],
    "create_branch_arms": ["create_branch_arms"],
    "create_elements": ["create_elements"],

    "fetch_arm_control_terminology": ["fetch_arm_control_terminology"],
    "fetch_epoch_control_terminology": ["fetch_epoch_control_terminology"],
    "fetch_branch_arm_control_terminology": ["fetch_branch_arm_control_terminology"],
    "fetch_element_control_terminology": ["fetch_element_control_terminology"],
}

# Define dependencies between high-level goals.
TASK_DEPENDENCIES = {
    "create_study_arms": ["create_study"],
    "create_epochs": ["create_study"],
    "create_branch_arms": ["create_study_arms"],
    "create_elements": ["create_study"],

    # Each fetch must wait for its corresponding create
    "fetch_arm_control_terminology": ["create_study_arms"],
    "fetch_epoch_control_terminology": ["create_epochs"],
    "fetch_branch_arm_control_terminology": ["create_branch_arms"],
    "fetch_element_control_terminology": ["create_elements"],
}
