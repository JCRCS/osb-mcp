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
        {"name": "create_design_cell", "description": "Defines study Design Cells."},
        {"name": "create_element", "description": "Adds elements to a study."},
        {"name": "fetch_arm_control_terminology", "description": "Retrieves control terminology for arms."},
        {"name": "fetch_epoch_control_terminology", "description": "Retrieves control terminology for epochs."},
        {"name": "fetch_element_control_terminology", "description": "Retrieves control terminology for elements."},
    ]
}
