import asyncio
import logging
from fastapi.responses import StreamingResponse
from fastapi import Request
import httpx
from osb_agent_app.agent import run_llm_driven_workflow
from mcp.server.fastmcp import FastMCP
import time

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# API Endpoints
API_URL = "http://127.0.0.1:9000"
OPEN_STUDY_BUILDER_URL = "http://127.0.0.1:9001"  # <- fixed typo here

# Initialize MCP server
mcp = FastMCP("OSB-MCP-Server", description="MCP Server providing access to Open Study Builder studies and general API utilities.")

@mcp.tool(description="Retrieve a list of studies from the Open Study Builder (OSB) API.")
def get_studies() -> dict:
    """
    Fetches all studies from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all studies metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/studies?page_number=1&page_size=0")
    time.sleep(7)
    return resp.json()

@mcp.tool(description="""BEFORE creating a study execute GET studies to generate unique properties. Create a new study in the Open Study Builder (OSB). BEFORE GET studies to generate unique properties
          Parameters:
        -   {"project_number": CDISC DEV, 
            "study_acronym": ["string", "Acronym of the study should be unique across studies"]
            "study_number": ["string","Number of the study should be a 4 digit number.", "It's unique, check into the existent studies"]
            }

          
          """)
async def create_study( study_acronym:str, study_number: str) -> dict:
    """
    Before using create_study, get studies to check uniqueness. Creates a new study inside the Open Study Builder.

    Parameters:
    -   {"project_number": CDISC DEV, 
        "study_acronym": ["string", "Acronym of the study should be unique across studies"]
        "study_number": ["string","Number of the study should be a 4 digit number.", "It's unique, check into the existent studies"]
        }

    a good example is
        {
        "study_acronym": "study_acronym", 
        "study_number": "1117"
        }

    Returns:
    - dict: Information about the newly created study or any error.
    """
    resp = httpx.post(f"{OPEN_STUDY_BUILDER_URL}/studies", json={
        "project_number": "CDISC DEV", 
        "study_acronym": study_acronym, 
        "study_number": study_number
    })
    # await asyncio.sleep(1000)
    time.sleep(7)
    return resp.json()


@mcp.tool(description="Retrieve a list of types of arms from the Open Study Builder (OSB) API.")
def fetch_arm_control_terminology() -> dict:
    """
    Fetches all types of arms from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all arm types metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms?page_size=100&sort_by=%7B%22name.sponsor_preferred_name%22:true%7D&codelist_name=Arm+Type")
    time.sleep(7)
    return resp.json()


@mcp.tool(description="Create a new study Arm in the Open Study Builder (OSB). Be sure that first get the fetch_arm_control_terminology to get the arm types")
def create_arm(study_uid, name, short_name, code, description, color, randomization_group, number_of_subjects, arm_type_uid, study_arm_data: dict) -> dict:
    """
    Creates a new study Arm inside the Open Study Builder.

    Parameters:
    - study_uid: study where it's the arm that the user wants to create
    - study_data (dict): The study arm to be created. Must follow the Open Study Builder schema.
    * {
            "name": "string",
            "short_name": "string",
            "code": "string",
            "description": "string",
            "arm_colour": "string",
            "randomization_group": "string",
            "number_of_subjects": 0,
            "arm_type_uid": "string"
        }

    Returns:
    - dict: Information about the newly created study arm or any error.
    """
    resp = httpx.post(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-arms",json={
        "name": name,
        "short_name": short_name,
        "code": code,
        "description": description,
        "arm_colour": color,
        "randomization_group": randomization_group,
        "number_of_subjects": number_of_subjects,
        "arm_type_uid": arm_type_uid
    })
    time.sleep(7)
    return resp.json()


@mcp.tool(description="Retrieve a list of epochs from the Open Study Builder (OSB) API.")
def fetch_epoch_control_terminology() -> dict:
    """
    Fetches all epochs from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all epoch metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/epochs/allowed-configs")
    time.sleep(7)
    return resp.json()

@mcp.tool(description="Retrieve a list of sub types of epochs from the Open Study Builder (OSB) API.")
def fetch_epoch_sub_type_control_terminology() -> dict:
    """
    Fetches all types of epochs from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all epoch types metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms?page_size=100&sort_by=%7B%22name.sponsor_preferred_name%22:true%7D&codelist_name=Epoch+Sub+Type")
    time.sleep(7)
    return resp.json()


@mcp.tool(description="Preview a study Epoch in the Open Study Builder (OSB) so it will generate the needed fields to create an epoch. Me sure that first get the fetch epoch control terminologies to get the subtype")
def preview_epoch(
        study_uid,
        epoch_subtype,) -> dict:
    """
    Preview a new study Epoch inside the Open Study Builder.

    Parameters:
    - study_uid: study where it's the epoch that the user wants to create
    - study_data (dict): The study epoch to be created. Must follow the Open Study Builder schema.
    * {
            "study_uid": "string",
            "epoch_subtype": "string epoch subtype uid control terminology",
        }

    Returns:
    - dict: Information about the newly created study epoch or any error.
    """
    resp = httpx.post(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-epochs/preview",json={
            "study_uid":study_uid,
            "epoch_subtype":epoch_subtype,
    })
    time.sleep(7)
    return resp.json()


@mcp.tool(description="Create a new study Epoch in the Open Study Builder (OSB). Be sure that first get the preview_epoch to get the epoch type, and epoch")
def create_epoch(
        study_uid,
        start_rule,
        end_rule,
        epoch,
        epoch_subtype,
        duration_unit,
        order,
        description,
        duration,
        color_hash) -> dict:
    """
    Creates a new study Epoch inside the Open Study Builder.

    Parameters:
    - study_uid: study where it's the epoch that the user wants to create
    - study_data (dict): The study epoch to be created. Must follow the Open Study Builder schema.
    * {
            "study_uid": "string",
            "start_rule": "string",
            "end_rule": "string",
            "epoch": "string epoch uid control terminology ",
            "epoch_subtype": "string epoch subtype uid control terminology",
            "duration_unit": "string",
            "order": 0,
            "description": "string",
            "duration": 0,
            "color_hash": "#FFFFFF"
        }

    Returns:
    - dict: Information about the newly created study epoch or any error.
    """
    resp = httpx.post(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-epochs",json={
            "study_uid":study_uid,
            "start_rule":start_rule,
            "end_rule":end_rule,
            "epoch":epoch,
            "epoch_subtype":epoch_subtype,
            "duration_unit":duration_unit,
            "order":order,
            "description":description,
            "duration":duration,
            "color_hash":color_hash,
    })
    time.sleep(7)
    return resp.json()


@mcp.tool(description="Retrieve a list of types of elements from the Open Study Builder (OSB) API.")
def fetch_element_control_terminology() -> dict:
    """
    Fetches all types of elements from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all element types metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms?page_size=100&sort_by=%7B%22name.sponsor_preferred_name%22:true%7D&codelist_name=Element+Type")
    time.sleep(7)
    return resp.json()


@mcp.tool(description="Create a new study Element in the Open Study Builder (OSB). Me sure that first get the fetch_element_control_terminology to get the element types")
def create_element(study_uid, 
                name,
                short_name,
                code,
                description,
                start_rule,
                end_rule,
                element_colour,
                element_subtype_uid,
    ) -> dict:
    """
    Creates a new study Element inside the Open Study Builder.

    Parameters:
    - study_uid: study where it's the element that the user wants to create
    - study_data (dict): The study element to be created. Must follow the Open Study Builder schema.
    * {
        "name": "string",
        "short_name": "string",
        "code": "string",
        "description": "string",
        "start_rule": "string",
        "end_rule": "string",
        "element_colour": "string",
        "element_subtype_uid": "string element subtype uid control terminology "
        }

    Returns:
    - dict: Information about the newly created study element or any error.
    """
    resp = httpx.post(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-elements",json={        
        "name": name,
        "short_name": short_name,
        "code": code,
        "description": description,
        "start_rule": start_rule,
        "end_rule": end_rule,
        "element_colour": element_colour,
        "element_subtype_uid": element_subtype_uid,
    })
    time.sleep(7)
    return resp.json()





@mcp.tool(description="Create a new study Design Cell in the Open Study Builder (OSB). Make sure that first you have the Study_arm_uid, study_element_uid, study_epoch_uid")
def create_design_cell(study_uid, 
        study_arm_uid,
        study_epoch_uid,
        study_element_uid,
        transition_rule,
        order,
    ) -> dict:
    """
    Creates a new study Design Cell inside the Open Study Builder.

    Parameters:
    - study_uid: study where it's the Design Cell that the user wants to create
    - study_data (dict): The study Design Cell to be created. Must follow the Open Study Builder schema.
    * {
        "study_arm_uid": "string",
        "study_branch_arm_uid": "string",
        "study_epoch_uid": "string",
        "study_element_uid": "string",
        "transition_rule": "string",
        "order": 0
        }

    Returns:
    - dict: Information about the newly created study Design Cell or any error.
    """
    resp = httpx.post(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-design-cells",json={        
        "study_arm_uid":  study_arm_uid,
        "study_epoch_uid":  study_epoch_uid,
        "study_element_uid":  study_element_uid,
        "transition_rule":  transition_rule,
        "order": order,
    })
    time.sleep(7)
    return resp.json()

@mcp.tool(description="""
    Generate the plan from the user request. First understand the goal and then it breaks don't into steps to interact with Open Study Builder correctly
    """)
def mcp_plan(user_request: str) -> dict:
    """
    Takes the user_request.
    Returns the step-by-step plan List.
    """
    # Execute the agent’s workflow
    results = run_llm_driven_workflow(user_request)
    time.sleep(7)
    return results#.json()

# Server startup logging
logging.info("Starting OSB FastMCP Server via STDIO...")

if __name__ == "__main__":
    logging.info("OSB FastMCP Server is now listening for connections over STDIO.")
    # Exposes an SSE endpoint at http://127.0.0.1:6274/sse
    mcp.run(transport="stdio")
