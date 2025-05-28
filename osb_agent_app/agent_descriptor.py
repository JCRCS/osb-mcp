# osb_agent_app/agent_descriptor.py

"""
Describes the OSB agent for discovery via the MCP core.
"""

AGENT_DESCRIPTOR = {
    "agent_name": "osb-builder",
    "description": "Designs clinical trials: studies, arms, epochs, elements, and fetches control terminology.",
    "tools": [
        {"name": "create_study", "description": "Creates a new clinical study record."},
        {"name": "get_study", "description": "Get the study by the study_uid"},
        {"name": "create_study_arm", "description": "Adds study arms to a study."},
        {"name": "preview_epoch", "description": "Defines study epochs."},
        {"name": "create_epoch", "description": "Defines study epochs."},
        {"name": "fetch_activity_type_terminology", "description": "Retrieves control terminology for activity type."},
        {"name": "fetch_activity_group_control_terminology", "description": "Retrieves control terminology for activity groups."},
        {"name": "fetch_activity_sub_group_control_terminology", "description": "Retrieves control terminology for actviity sub groups."},
        {"name": "fetch_soa_group_control_terminology", "description": "Retrieves control terminology for activity schedule of activities groups."},
        {"name": "create_study_activity", "description": "Defines study activities."},
        {"name": "get_study_activity", "description": "get study activities that exists."},
        {"name": "create_activity_schedule", "description": "Defines create visit activity schedule."},
        {"name": "create_design_cell", "description": "Defines study Design Cells."},
        {"name": "create_element", "description": "Adds elements to a study."},
        {"name": "fetch_arm_control_terminology", "description": "Retrieves control terminology for arms."},
        {"name": "fetch_epoch_control_terminology", "description": "Retrieves control terminology for epochs."},
        {"name": "fetch_element_control_terminology", "description": "Retrieves control terminology for elements."},
        {"name": "preview_visit", "description": "Defines study visits."},
        {"name": "create_visit", "description": "Defines study visits."},
        {"name": "fetch_time_point_reference_control_terminology", "description": "Retrieves control terminology for time point reference types."},
        {"name": "fetch_visit_type_control_terminology", "description": "Retrieves control terminology for visits."},
        {"name": "get_study_visits", "description": "get study visits that exists."},
        {"name": "get_activity_schedule", "description": "get study activity schedule that exists."},
        {"name": "get_study_epochs", "description": "get study epochs that exists."},
        {"name": "get_activity_schedule", "description": "get study activity schedule that exists."},
    ]
}
