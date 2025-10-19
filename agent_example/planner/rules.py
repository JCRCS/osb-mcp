# Map each high-level goal to its list of atomic tasks.
PLANNER_RULES = {
    "get_studies": ["get_studies"],
    "create_study": ["create_study"],
    "create_study_arm": ["create_study_arm"],
    "create_epoch": ["create_epoch"],
    "create_study_activity": ["create_study_activity"],
    "get_study_activity": ["get_study_activity"],
    "preview_epoch": ["preview_epoch"],
    "get_epochs": ["get_epochs"],
    "create_element": ["create_element"],
    "create_design_cell": ["create_design_cell"],
    "create_activity_schedule": ["create_activity_schedule"],
    "get_activity_schedule": ["get_activity_schedule"],
    "create_visit": ["create_visit"],
    "preview_visit": ["preview_visit"],
    "fetch_visit_control_terminology": ["fetch_visit_control_terminology"],
    "fetch_time_point_reference_control_terminology": [
        "fetch_time_point_reference_control_terminology"
    ],
    "fetch_visit_contact_mode_terminology": [
        "fetch_visit_contact_mode_terminology"
    ],  # TODO
    "fetch_visit_epoch_allocation_type_terminology": [
        "fetch_visit_epoch_allocation_type_terminology"
    ],  # TODO
    "get_activity_schedule": ["get_activity_schedule"],
    "get_study_visits": ["get_study_visits"],
    "fetch_arm_control_terminology": ["fetch_arm_control_terminology"],
    "fetch_epoch_control_terminology": ["fetch_epoch_control_terminology"],
    "fetch_activity_type_terminology": ["fetch_activity_type_terminology"],
    "fetch_soa_group_control_terminology": ["fetch_soa_group_control_terminology"],
    "fetch_element_control_terminology": ["fetch_element_control_terminology"],
}

# Define dependencies between high-level goals.
TASK_DEPENDENCIES = {
    "create_study": ["get_studies"],
    "create_study_arm": ["create_study", "fetch_arm_control_terminology"],
    "preview_epoch": ["create_study", "fetch_epoch_control_terminology"],
    "create_epoch": [
        "create_study",
        "fetch_epoch_control_terminology",
        "preview_epoch",
    ],
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
    "create_study_activity": [
        "create_study",
        "fetch_activity_type_terminology",
        "fetch_soa_group_control_terminology",
        "get_study_activity",
    ],
    "create_visit": [
        "create_study",
        "get_epochs",
        "create_epoch",
        "fetch_time_point_reference_control_terminology",
        "fetch_visit_contact_mode_terminology",  # TODO
        "fetch_visit_epoch_allocation_type_terminology",  # TODO
        "fetch_visit_control_terminology",
        "get_study_visits",
        "preview_visit",
    ],
    "create_element": ["create_study", "fetch_element_control_terminology"],
}


AVAILABLE_TASKS = [
    {
        "name": "get_studies",
        "description": "look for the existent studies, to check uniqueness",
        "agent": "study_agent",
    },
    {
        "name": "create_study",
        "description": "Perform the task of creating 1 'create_study'.",
        "agent": "study_agent",
    },
    {
        "name": "create_study_arm",
        "description": "Perform the task of creating 1 'create_study_arm'.",
        "agent": "study_arm_agent",
    },
    {
        "name": "create_epoch",
        "description": "Perform the task of creating 1 'create_epoch'.",
        "agent": "study_epoch_agent",
    },
    {
        "name": "preview_epoch",
        "description": "fills the needed data to perform the creation of the epoch Perform the task preview 1 'preview_epoch'.",
        "agent": "study_epoch_agent",
    },
    {
        "name": "create_element",
        "description": "Perform the task of creating 1 'create_element'.",
        "agent": "study_element_agent",
    },
    {
        "name": "fetch_arm_control_terminology",
        "description": "Perform the task 'fetch_arm_control_terminology'.",
        "agent": "study_arm_agent",
    },
    {
        "name": "fetch_epoch_control_terminology",
        "description": "Perform the task 'fetch_epoch_control_terminology'.",
        "agent": "study_epoch_agent",
    },
    {
        "name": "fetch_element_control_terminology",
        "description": "Perform the task 'fetch_element_control_terminology'.",
        "agent": "study_element_agent",
    },
    {
        "name": "fetch_activity_type_terminology",
        "description": "Retrieves control terminology for activity type.",
        "agent": "study_activity_agent",
    },
    {
        "name": "fetch_soa_group_control_terminology",
        "description": "Retrieves control terminology for activity schedule of activities groups.",
        "agent": "study_activity_agent",
    },
    {
        "name": "create_study_activity",
        "description": "Defines study activities.",
        "agent": "study_activity_agent",
    },
    {
        "name": "get_study_activity",
        "description": "get study activities to check uniqueness.",
        "agent": "study_activity_agent",
    },
    {
        "name": "create_activity_schedule",
        "description": "Defines create visit activity schedule",
        "agent": "study_schedule_agent",
    },
    {
        "name": "get_activity_schedule",
        "description": "gets visit activity schedule",
        "agent": "study_schedule_agent",
    },
    {
        "name": "create_design_cell",
        "description": "Defines create design cell",
        "agent": "study_design_agent",
    },
    {
        "name": "create_visit",
        "description": "Perform the task of creating 1 'create_visit'.",
        "agent": "study_visit_agent",
    },
    {
        "name": "preview_visit",
        "description": "fills the needed data to perform the creation of the visit Perform the task preview 1 'preview_visit'.",
        "agent": "study_visit_agent",
    },
    {
        "name": "fetch_time_point_reference_control_terminology",
        "description": "Perform the task 'fetch_time_point_reference_control_terminology'.",
        "agent": "study_visit_agent",
    },
    {
        "name": "fetch_visit_contact_mode_terminology",
        "description": "Perform the task 'fetch_visit_contact_mode_terminology'.",
        "agent": "study_visit_agent",
    },  # TODO
    {
        "name": "fetch_visit_epoch_allocation_type_terminology",
        "description": "Perform the task 'fetch_visit_epoch_allocation_type_terminology'.",
        "agent": "study_visit_agent",
    },  # TODO
    {
        "name": "fetch_visit_control_terminology",
        "description": "Perform the task 'fetch_visit_control_terminology'.",
        "agent": "study_visit_agent",
    },
    {
        "name": "get_study_visits",
        "description": "get study visits to check uniqueness in timeline.",
        "agent": "study_visit_agent",
    },
    {
        "name": "get_epochs",
        "description": "get study epochs to fill the visits data.",
        "agent": "study_epoch_agent",
    },
    {
        "name": "get_activity_schedule",
        "description": "get study visits activity schedules to check uniqueness in timeline.",
        "agent": "study_schedule_agent",
    },
]


SUB_AGENT_MAP = {
    "Product_out_line_sub_agent": [
        "study_agent",
        "study_arm_agent",
        "study_epoch_agent",
        "study_visit_agent",
        "study_element_agent",
        "study_design_agent",
    ],
    "Schedule_of_Activitites_sub_agent": [
        "study_activity_agent",
        "study_schedule_agent",
    ],
}