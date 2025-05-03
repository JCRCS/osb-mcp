# osb_agent_app/agent_descriptor.py

"""
Describes the OSB agent for discovery via the MCP core.
"""

AGENT_DESCRIPTOR = {
    "agent_name": "osb-builder",
    "description": "Designs clinical trials: studies, arms, epochs, elements, and fetches control terminology.",
    "tools": [
        {"name": "create_study", "description": "Creates a new clinical study record."},
        {"name": "create_study_arms", "description": "Adds study arms to a study."},
        {"name": "create_epochs", "description": "Defines study epochs."},
        {"name": "create_branch_arms", "description": "Defines branch arms for arms."},
        {"name": "create_elements", "description": "Adds elements to a study."},
        {"name": "fetch_arm_control_terminology", "description": "Retrieves control terminology for arms."},
        {"name": "fetch_epoch_control_terminology", "description": "Retrieves control terminology for epochs."},
        {"name": "fetch_branch_arm_control_terminology", "description": "Retrieves control terminology for branch arms."},
        {"name": "fetch_element_control_terminology", "description": "Retrieves control terminology for elements."},
    ]
}
