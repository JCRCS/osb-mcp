import asyncio
import logging
from fastapi.responses import StreamingResponse
from fastapi import Request
import httpx
from mcp.server.fastmcp import FastMCP

# Setup basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# API Endpoints
API_URL = "http://127.0.0.1:9000"
OPEN_STUDY_BUILDER_URL = "http://127.0.0.1:9001"  # <- fixed typo here

# Initialize MCP server
mcp = FastMCP("OSB-MCP-Server", description="MCP Server providing access to Open Study Builder studies and general API utilities.")

# @mcp.resource("greeting://", description="Retrieve a greeting message from the API Proxy service.")
# def get_greeting() -> str:
#     """Returns a greeting message."""
#     resp = httpx.get(f"{API_URL}/greet")
#     return resp.json()["message"]

# @mcp.tool(description="Set user information like name and country into the API Proxy service.")
# def set_info(name: str, country: str) -> dict:
#     """
#     Sets user information (name and country) into the proxy API.
    
#     Parameters:
#     - name (str): The user's name.
#     - country (str): The user's country.
    
#     Returns:
#     - dict: Confirmation and stored info.
#     """
#     resp = httpx.post(f"{API_URL}/info", json={"name": name, "country": country})
#     return resp.json()

@mcp.tool(description="Retrieve a list of studies from the Open Study Builder (OSB) API.")
def get_studies() -> dict:
    """
    Fetches all studies from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all studies metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/studies")
    return resp.json()

@mcp.tool(description="Create a new study in the Open Study Builder (OSB).")
def create_study(study_data: dict) -> dict:
    """
    Creates a new study inside the Open Study Builder.

    Parameters:
    - study_data (dict): The study definition to be created. Must follow the Open Study Builder schema.

    Returns:
    - dict: Information about the newly created study or any error.
    """
    resp = httpx.post(f"{OPEN_STUDY_BUILDER_URL}/studies", json=study_data)
    return resp.json()

@mcp.tool(description="Create a new study Arm in the Open Study Builder (OSB).")
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
    return resp.json()

# @mcp.resource("country://{name}", description="Get the country associated with a specific user name from the API Proxy service.")
# def get_country(name: str) -> str:
#     """Returns the country associated with a given user name."""
#     resp = httpx.get(f"{API_URL}/country/{name}")
#     if resp.status_code == 404:
#         return f"No info for {name}"
#     return resp.json()["country"]

# Server startup logging
logging.info("Starting OSB FastMCP Server via STDIO...")

if __name__ == "__main__":
    logging.info("OSB FastMCP Server is now listening for connections over STDIO.")
    # Exposes an SSE endpoint at http://127.0.0.1:6274/sse
    mcp.run(transport="stdio")
