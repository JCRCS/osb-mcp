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



from pydantic import BaseModel, RootModel
from typing import List

class Content(BaseModel):
    soa_group_term_uid: str
    activity_uid: str
    order: str
    activity_group_uid: str
    activity_subgroup_uid: str

class RequestItem(BaseModel):
    method: str
    content: Content

class RequestList(RootModel[List[RequestItem]]):
    pass


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
    time.sleep(1)
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
    time.sleep(1)
    return resp.json()


@mcp.tool(description="Retrieve a list of types of arms from the Open Study Builder (OSB) API.")
def fetch_arm_control_terminology() -> dict:
    """
    Fetches all types of arms from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all arm types metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms?page_size=100&sort_by=%7B%22name.sponsor_preferred_name%22:true%7D&codelist_name=Arm+Type")
    time.sleep(1)
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
    time.sleep(1)
    return resp.json()


# @mcp.tool(description="""
#         Retrieve a list of visits contact modes from the Open Study Builder (OSB) API.
#         In order that the other agent can unerstand you, return a tuple with:
#         - term_uid and sponsor_preferred_name
#           """)
# def fetch_visit_contact_mode_terminology() -> dict:
#     """
#     Fetches all  visit contact modes from the Open Study Builder.

#     Returns:
#     - dict: A dictionary containing all  visits contact modes metadata.

#     In order that the other agent can unerstand you, return a tuple with:
#     - term_uid and sponsor_preferred_name
#     """
#     resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms?page_size=100&sort_by=%7B%22name.sponsor_preferred_name%22:true%7D&codelist_name=Visit+Contact+Mode")
#     time.sleep(1)
#     return resp.json()



# @mcp.tool(description="""
#         Retrieve a list of visits repeating frequency types from the Open Study Builder (OSB) API.     
#         In order that the other agent can unerstand you, return a tuple with:
#         - term_uid and sponsor_preferred_name
#           """)
# def fetch_visit_repeating_frequency_type_terminology() -> dict:
#     """
#     Fetches all  visit repeating frequency types from the Open Study Builder.

#     Returns:
#     - dict: A dictionary containing all  visits repeating frequency types metadata.

#     In order that the other agent can unerstand you, return a tuple with:
#     - term_uid and sponsor_preferred_name
#     """
#     resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms?page_size=100&sort_by=%7B%22name.sponsor_preferred_name%22:true%7D&codelist_name=Repeating+Visit+Frequency")
#     time.sleep(1)
#     return resp.json()




# @mcp.tool(description="""
#           Retrieve a list of visit's phase/epoch allocation from the Open Study Builder (OSB) API.
#           In order that the other agent can understand you, return a tuple with:
#             - term_uid and sponsor_preferred_name
#           """)
# def fetch_visit_epoch_allocation_type_terminology() -> dict:
#     """
#     Fetches all  visit phase/epoch allocation types from the Open Study Builder.

#     Returns:
#     - dict: A dictionary containing all phase/epoch allocation frequency types metadata.

#     In order that the other agent can unerstand you, return a tuple with:
#     - term_uid and sponsor_preferred_name
#     """
#     resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms?page_size=100&sort_by=%7B%22name.sponsor_preferred_name%22:true%7D&codelist_name=Epoch+Allocation")
#     time.sleep(1)
#     return resp.json()


@mcp.tool(description="""Retrieve a list of study epochs from the Open Study Builder (OSB) API. 
          get epoch as epoch uid and the epoch_name to so it can be used on preview_visit""")
def get_study_epochs(
        study_uid:str,
) -> dict:
    """
    Fetches all studies from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all studies metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-epochs?page_size=0")
    time.sleep(1)
    return resp.json()


@mcp.tool(description="""Retrieve a list of study visit from the Open Study Builder (OSB) API. 
          get the visit name, the visit time value, the visit type unit and the epoch uid to check uniqueness on the timeline to assign the time value on preview_visit""")
def get_study_visits(
        study_uid:str,
) -> dict:
    """
    Fetches all studies from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all studies metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-visits?page_size=50&sort_by=%7B%22order%22:false%7D")
    time.sleep(1)
    return resp.json()

@mcp.tool(description="""
        Retrieve a list of types of visits from the Open Study Builder (OSB) API.
        In order that the other agent can understand you, return a tuple with:
        - term_uid and sponsor_preferred_name
          """)
def fetch_visit_type_control_terminology() -> dict:
    """
    Fetches all types of visits from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all visit types metadata.

    In order that the other agent can unerstand you, return a tuple with:
    - term_uid and sponsor_preferred_name
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms/names?page_size=0&codelist_name=VisitType")
    time.sleep(1)
    return resp.json()



@mcp.tool(description="""
        Retrieve a list of time point reference types from the Open Study Builder (OSB) API.
        In order that the other agent can understand you, return a tuple with:
            - term_uid and sponsor_preferred_name
        """)
def fetch_time_point_reference_control_terminology() -> dict:
    """
    Fetches all time point reference types of the Open Study Builder.

    Returns:
    - dict: A dictionary containing all time point reference types metadata.

    In order that the other agent can understand you, return a tuple with:
    - term_uid and sponsor_preferred_name
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms?page_size=100&sort_by=%7B%22name.sponsor_preferred_name%22:true%7D&codelist_name=Time+Point+Reference")
    time.sleep(1)
    return resp.json()

@mcp.tool(description="""
          Preview a study visit in the Open Study Builder (OSB) so it will generate the needed fields to create an visit. 
          Be sure that first fetch_visit_type_control_terminology to get the visit type """)
def preview_visit(
        study_uid:str,
        is_global_anchor_visit:str,
        # visit_class:str,
        # show_visit:str,
        # min_visit_window_value:str,
        # max_visit_window_value:str,
        # visit_subclass:str,
        # visit_window_unit_uid:str,
        study_epoch_uid:str,
        # epoch_allocation_uid:str,
        time_value:str,
        time_reference_uid:str,
        visit_type_uid:str,
        # visit_contact_mode_uid:str,
        # time_unit_uid:str,
) -> dict:
    """
    Preview a new study visit inside the Open Study Builder.

    Parameters:
    - study_uid: study where it's the visit that the user wants to create
    - study_data (dict): The study visit to be created. Must follow the Open Study Builder schema.
    * {
        "is_global_anchor_visit":false,
        "visit_class":"SINGLE_VISIT",
        "show_visit":true,
        "min_visit_window_value":0,
        "max_visit_window_value":0,
        "visit_subclass":"SINGLE_VISIT",
        "visit_window_unit_uid":"UnitDefinition_000365",
        "study_epoch_uid":"StudyEpoch_000039",
        "epoch_allocation_uid":"CTTerm_000192",
        "time_value":0,
        "time_reference_uid":"CTTerm_000119",
        "visit_type_uid":"CTTerm_000190",
        "visit_contact_mode_uid":"CTTerm_000079",
        "time_unit_uid":"UnitDefinition_000365"
    }

    Returns:
    - dict: Information about the newly created study visit or any error.
    """
    resp = httpx.post(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-visits/preview",json={
        "is_global_anchor_visit":is_global_anchor_visit,
        "visit_class":"SINGLE_VISIT",
        "show_visit":True,
        "min_visit_window_value":0,
        "max_visit_window_value":0,
        "visit_subclass":"SINGLE_VISIT",
        "visit_window_unit_uid":"UnitDefinition_000365",
        "study_epoch_uid":study_epoch_uid,
        "epoch_allocation_uid":"CTTerm_000192",
        "time_value":time_value,
        "time_reference_uid":time_reference_uid,
        "visit_type_uid":visit_type_uid,
        "visit_contact_mode_uid":"CTTerm_000079",
        "time_unit_uid":"UnitDefinition_000365",
    })
    time.sleep(1)
    return resp.json()


@mcp.tool(description="""
          Create a new study visit in the Open Study Builder (OSB). 
          Be sure that first get the preview_visit to get all the properties. If the preview doesn't succeed retry the preview to get the parameters. 
          """)
def create_visit(
        study_uid,
        is_global_anchor_visit,
        visit_class,
        show_visit,
        min_visit_window_value,
        max_visit_window_value,
        visit_subclass,
        visit_window_unit_uid,
        study_epoch_uid,
        epoch_allocation_uid,
        time_value,
        time_reference_uid,
        visit_type_uid,
        visit_contact_mode_uid,
        is_soa_milestone,
        study_day_label,
        study_week_label,
        description,
        time_unit_uid,
    ) -> dict:
    """
    Creates a new study visit inside the Open Study Builder.

    Parameters:
    - study_uid: study where it's the visit that the user wants to create
    - study_data (dict): The study visit to be created. Must follow the Open Study Builder schema.
    * {
        "is_global_anchor_visit":true,
        "visit_class":"SINGLE_VISIT",
        "show_visit":true,
        "min_visit_window_value":0,
        "max_visit_window_value":0,
        "visit_subclass":"SINGLE_VISIT",
        "visit_window_unit_uid":"UnitDefinition_000365",
        "study_epoch_uid":"StudyEpoch_000039",
        "epoch_allocation_uid":"CTTerm_000192",
        "time_value":0,
        "time_reference_uid":"CTTerm_000119",
        "visit_type_uid":"CTTerm_000190",
        "visit_contact_mode_uid":"CTTerm_000079",
        "is_soa_milestone":true,
        "study_day_label":"Day 1",
        "study_week_label":"Week 1",
        "description":"test",
        "time_unit_uid":"UnitDefinition_000365"
    }

    Returns:
    - dict: Information about the newly created study visit or any error.
    """
    resp = httpx.post(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-visits",json={
            "is_global_anchor_visit":is_global_anchor_visit,
            "visit_class":visit_class,
            "show_visit":show_visit,
            "min_visit_window_value":min_visit_window_value,
            "max_visit_window_value":max_visit_window_value,
            "visit_subclass":visit_subclass,
            "visit_window_unit_uid":visit_window_unit_uid,
            "study_epoch_uid":study_epoch_uid,
            "epoch_allocation_uid":epoch_allocation_uid,
            "time_value":time_value,
            "time_reference_uid":time_reference_uid,
            "visit_type_uid":visit_type_uid,
            "visit_contact_mode_uid":visit_contact_mode_uid,
            "is_soa_milestone":is_soa_milestone,
            "study_day_label":study_day_label,
            "study_week_label":study_week_label,
            "description":description,
            "time_unit_uid":time_unit_uid,
    })
    time.sleep(1)
    return resp.json()


@mcp.tool(description="Retrieve a list of epochs from the Open Study Builder (OSB) API.")
def fetch_epoch_control_terminology() -> dict:
    """
    Fetches all epochs from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all epoch metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/epochs/allowed-configs")
    time.sleep(1)
    return resp.json()

@mcp.tool(description="Retrieve a list of sub types of epochs from the Open Study Builder (OSB) API.")
def fetch_epoch_sub_type_control_terminology() -> dict:
    """
    Fetches all types of epochs from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all epoch types metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms?page_size=100&sort_by=%7B%22name.sponsor_preferred_name%22:true%7D&codelist_name=Epoch+Sub+Type")
    time.sleep(1)
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
    time.sleep(1)
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
    time.sleep(1)
    return resp.json()




@mcp.tool(description="""
          Retrieve a list of possible activity types from the Open Study Builder (OSB) API.

          The response structure is:
            {
                "items": [
                    {
                    "start_date": "string",
                    "end_date": "string",
                    "status": "string",
                    "version": "string",
                    "change_description": "string",
                    "author_username": "string",
                    "uid": "string",
                    "name": "string",
                    "name_sentence_case": "string",
                    "definition": "string",
                    "abbreviation": "string",
                    "library_name": "string",
                    "possible_actions": [
                        "string"
                    ],
                    "nci_concept_id": "string",
                    "nci_concept_name": "string",
                    "activity_groupings": [
                        {
                            "activity_group_uid": "uid_0001",
                            "activity_group_name": "group name",
                            "activity_subgroup_uid": "uid_0002",
                            "activity_subgroup_name": "sub group name"
                        }
                    ],
                    "activity_instances": [],
                    "synonyms": [
                        "string"
                    ],
                    "request_rationale": "string",
                    "is_request_final": false,
                    "is_request_rejected": false,
                    "contact_person": "string",
                    "reason_for_rejecting": "string",
                    "requester_study_id": "string",
                    "replaced_by_activity": "string",
                    "is_data_collected": false,
                    "is_multiple_selection_allowed": true,
                    "is_finalized": false,
                    "is_used_by_legacy_instances": false
                    }
                ],
                "total": 0,
                "page": 0,
                "size": 0
                }
          
          you need to generate an output of activity_group_uid, activity_group_name, activity_subgroup_uid, activity_subgroup_name and activity name in triples so the agent can detect which activity to select
    """)
def fetch_activity_type_terminology() -> dict:
    """
    Fetches all types of activities types from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all activity type metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/concepts/activities/activities?library_name=Sponsor&page_number=1&page_size=10&filters=%7B%22%2A%22%3A%7B%20%22v%22%3A%20%5B%22%22%5D%2C%20%22op%22%3A%20%22co%22%7D%7D&operator=and&total_count=false")
    time.sleep(1)
    return resp.json()


@mcp.tool(description="Retrieve a list of types of soa group terms from the Open Study Builder (OSB) API.")
def fetch_soa_group_control_terminology() -> dict:
    """
    Fetches all types of activities from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all activity types metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms?page_size=100&sort_by=%7B%22name.sponsor_preferred_name%22:true%7D&codelist_name=Flowchart+Group")
    time.sleep(1)
    return resp.json()

@mcp.tool(description="Retrieve a list of study activities from the Open Study Builder (OSB) API. get the activity name, the activity group uid and the activity sub group uid to check uniqueness")
def get_study_activities(
        study_uid:str,
) -> dict:
    """
    Fetches all studies from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all studies metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-activities?page_size=0")
    time.sleep(1)
    return resp.json()

@mcp.tool(description=""" 
        Before using create_study_activity, get get_study_activities to check uniqueness on                   
            - activity_subgroup_uid, 
            - activity_group_uid, 
            - activity's name triple. 
        Create a new study activity in the Open Study Builder (OSB).
        Be sure that first get the 
            - fetch_soa_group_control_terminology, 
            - fetch_activity_sub_group_control_terminology, 
            - fetch_activity_group_control_terminology, 
            - fetch_activity_type_terminology 
        to get the needed data to create an activity
          
        The needed fetch_activity_sub_group_control_terminology and fetch_activity_group_control_terminology must match with the fetch_activity_type_terminology groupings 
          
        
        """)
def create_study_activity(
        study_uid:str,
        soa_group_term_uid:str,
        activity_uid:str,
        order:str,
        activity_group_uid:str,
        activity_subgroup_uid:str,
        # method:str,
        ) -> dict:
    """
    Creates a new study activity inside the Study. Where the Study Activity is an instantiation of an Activity define in the library storage. 

    In order to create the activity you need to know:
        - activity types
        - activity sub groups
        - activity groups
        - activity soa group types
    
    the Study Activity have a unique triple of:
        - activity type names
        - activity sub groups
        - activity groups

    the Study Activity can just have activity sub groups and activity groups that the activity type has in the activity groupings

    Parameters:
    - study_uid: study where it's the activity that the user wants to create
    - study_data (dict): The study activity to be created. Must follow the Open Study Builder schema.
    * 
            [
            {
                "method":"POST",
                "content":
                    {
                    "soa_group_term_uid":"string uid",
                    "activity_uid":"string uid",
                    "order":"string",
                    "activity_group_uid":"string uid",
                    "activity_subgroup_uid":"string uid"
            }
            ]

    Returns:
    - dict: Information about the newly created study activity or any error.
    """
    payload = [
    {
        "method":"POST",
        "content":{
            "soa_group_term_uid":soa_group_term_uid,
            "activity_uid":activity_uid,
            "order":None,
            "activity_group_uid":activity_group_uid,
            "activity_subgroup_uid":activity_subgroup_uid,
        }
    }
    ]
    resp = httpx.post(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-activities/batch",json=payload)
    time.sleep(1)
    return resp.json()


@mcp.tool(description="Retrieve a list of types of elements from the Open Study Builder (OSB) API.")
def fetch_element_control_terminology() -> dict:
    """
    Fetches all types of elements from the Open Study Builder.

    Returns:
    - dict: A dictionary containing all element types metadata.
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/ct/terms?page_size=100&sort_by=%7B%22name.sponsor_preferred_name%22:true%7D&codelist_name=Element+Type")
    time.sleep(1)
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
    time.sleep(1)
    return resp.json()


@mcp.tool(description="""get study visit activity schedule in the Open Study Builder (OSB). 
          Get study visit activity schedule to check uniqueness 
          return the study_activity_uid and the study_visit_uid match its names on the get_study_activity and get_study_visits
          """)
def get_activity_schedule(study_uid, 
    ) -> dict:
    """
    get study visit activity schedules inside the Open Study Builder.

    Returns:
    - dict: Information about the newly get  study visit activity schedule or any error.

    
    """
    resp = httpx.get(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-activity-schedules?operational=false")
    time.sleep(1)
    return resp.json()

@mcp.tool(description="First get_activity_schedule inorder to create. Create a new study visit activity schedule in the Open Study Builder (OSB). Make sure that first you have the study visit activity, study visit ")
def create_activity_schedule(study_uid, 
        study_activity_uid,
        study_visit_uid,
    ) -> dict:
    """
    Creates a new study visit activity schedule inside the Open Study Builder.

    Parameters:
    - study_uid: study where it's the study visit activity schedule  that the user wants to create
    - study_data (dict): The study visit activity schedule to be created. Must follow the Open Study Builder schema.
    * {
        "study_activity_uid":"StudyActivity_000028",
        "study_visit_uid":"StudyVisit_000039"
    }


    Returns:
    - dict: Information about the newly created study visit activity schedule or any error.
    """
    resp = httpx.post(f"{OPEN_STUDY_BUILDER_URL}/studies/{study_uid}/study-activity-schedules",json={        
        "study_activity_uid":study_activity_uid,
        "study_visit_uid":study_visit_uid
    })
    time.sleep(1)
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
    time.sleep(1)
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
    time.sleep(1)
    return results#.json()

# Server startup logging
logging.info("Starting OSB FastMCP Server via STDIO...")

if __name__ == "__main__":
    logging.info("OSB FastMCP Server is now listening for connections over STDIO.")
    # Exposes an SSE endpoint at http://127.0.0.1:6274/sse
    mcp.run(transport="stdio")
