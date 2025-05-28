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
    "create_study_activity": ["create_study_activity"],
    "get_study_activity": ["get_study_activity"],
    "preview_epoch": ["preview_epoch"],
    "create_element": ["create_element"],
    "create_design_cell": ["create_design_cell"],

    "create_activity_schedule": ["create_activity_schedule"],
    "get_activity_schedule": ["get_activity_schedule"],
    "create_visit": ["create_visit"],
    "preview_visit": ["preview_visit"],
    "fetch_visit_control_terminology": ["fetch_visit_control_terminology"],
    "fetch_time_point_reference_control_terminology": ["fetch_time_point_reference_control_terminology"],
    "get_activity_schedule": ["get_activity_schedule"],
    "get_study_visits": ["get_study_visits"],
    "get_study_epoch": ["get_study_epoch"],

    "fetch_arm_control_terminology": ["fetch_arm_control_terminology"],
    "fetch_epoch_control_terminology": ["fetch_epoch_control_terminology"],
    "fetch_activity_type_terminology": ["fetch_activity_type_terminology"],
    "fetch_soa_group_control_terminology": ["fetch_soa_group_control_terminology"],
    "fetch_element_control_terminology": ["fetch_element_control_terminology"],
}

# Define dependencies between high-level goals.
TASK_DEPENDENCIES = {
    "create_study":["get_studies"],
    "create_study_arm": ["create_study","fetch_arm_control_terminology"],
    "preview_epoch": ["create_study", "fetch_epoch_control_terminology"],
    "create_epoch": ["create_study", "fetch_epoch_control_terminology","preview_epoch"],
    "create_design_cell": [
        "create_study",
        "create_study_arm",
        "create_epoch",
        "create_element",
    ],
    "create_activity_schedule": [
        "get_activity_schedule",
        "get_study_activity",
        "get_study_visits",
    ],
    #  "get_activity_schedule": [
    #     "get_study_activity",
    #     "get_study_visits",
    # ],
    "create_study_activity": [
        "create_study",
        "fetch_activity_type_terminology",
        "fetch_soa_group_control_terminology",
        "get_study_activity",
    ],
    "create_visit": [
        "create_study",
        "fetch_time_point_reference_control_terminology",
        "fetch_visit_control_terminology",
        "get_study_epoch",
        "get_study_visits",
        "preview_visit",
    ],
    "create_element": ["create_study", "fetch_element_control_terminology"],

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
