# osb_agent_app/planner_rules.py

"""
Defines high-level goal → atomic-task sequences and inter-goal dependencies.
"""

# Map each high-level goal to its list of atomic tasks.
PLANNER_RULES = {
    "get_studies":[],
    "create_study": ["create_study"],
    "create_study_arm": ["create_study_arm"],
    "create_epoch": ["create_epoch"],
    "create_branch_arm": ["create_branch_arm"],
    "create_element": ["create_element"],

    "fetch_arm_control_terminology": ["fetch_arm_control_terminology"],
    "fetch_epoch_control_terminology": ["fetch_epoch_control_terminology"],
    "fetch_element_control_terminology": ["fetch_element_control_terminology"],
}

# Define dependencies between high-level goals.
TASK_DEPENDENCIES = {
    "create_study":["get_studies"],
    "create_study_arm": ["create_study","fetch_arm_control_terminology"],
    "create_epoch": ["create_study", "fetch_epoch_control_terminology"],
    "create_branch_arm": ["create_study_arm"],
    "create_element": ["create_study", "fetch_element_control_terminology"],

    # Each fetch must wait for its corresponding create
    # "fetch_arm_control_terminology": [],
    # "fetch_epoch_control_terminology": [],
    # "fetch_element_control_terminology": [],
}

def requires_create_study(context):
    """
    Determines whether 'create_study' should be added based on the context.
    """
    return not context.get("study_uid")


def get_task_dependencies(task_name, context):
    """
    Returns dependencies for a given task based on the current context.
    """
    dependencies = []
    requires_create_study_bool = requires_create_study(context)

    if task_name in ["create_study_arms","create_epochs","create_branch_arms","create_element"]:
        if requires_create_study_bool:
            dependencies.append("create_study")
        dependencies.append("fetch_arm_control_terminology")

    if task_name == "create_epochs":
        dependencies.append("fetch_epoch_control_terminology")
        dependencies.append("fetch_epoch_type_control_terminology")
        dependencies.append("fetch_epoch_subtype_control_terminology")

    if task_name == "create_element":
        dependencies.append("fetch_element_control_terminology")
    
    if task_name == "create_branch_arms":
        dependencies.append("create_study_arms")


    # Add other task dependency logic here
    return dependencies
