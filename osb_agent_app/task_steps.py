# osb_agent_app/task_steps.py

def create_study(context: dict) -> dict:
    # e.g. POST /studies
    study = {"study_id": "STU123"}
    return {"study": study}

def create_study_arm(context: dict) -> dict:
    study = context.get("study", {})
    # e.g. POST /studies/{id}/arms
    arms = [{"arm_id": "ARM1"}, {"arm_id": "ARM2"}]
    return {"arms": arms}

def create_epoch(context: dict) -> dict:
    study = context.get("study", {})
    epochs = [{"epoch_id": "E1"}]
    return {"epochs": epochs}

def create_study_activity(context: dict) -> dict:
    study = context.get("study", {})
    activities = [{"activity_id": "E1"}]
    return {"activity": activities}

def fetch_study_activity(context: dict) -> dict:
    study = context.get("study", {})
    activities = [{"activity_id": "E1"}]
    return {"activity": activities}

def preview_epoch(context: dict) -> dict:
    study = context.get("study", {})
    epochs = [{"epoch_id": "E1"}]
    return {"epochs": epochs}

def create_visit(context: dict) -> dict:
    study = context.get("study", {})
    epochs = [{"epoch_id": "E1"}]
    return {"epochs": epochs}
def preview_visit(context: dict) -> dict:
    study = context.get("study", {})
    epochs = [{"epoch_id": "E1"}]
    return {"epochs": epochs}
def get_study_visits(context: dict) -> dict:
    study = context.get("study", {})
    activities = [{"activity_id": "E1"}]
    return {"activity": activities}
def get_study_epoch(context: dict) -> dict:
    study = context.get("study", {})
    activities = [{"activity_id": "E1"}]
    return {"activity": activities}
def fetch_visit_control_terminology(context: dict) -> dict:
    return {"visit_control_terms": ["Run-In", "Washout"]}
def fetch_time_point_reference_control_terminology(context: dict) -> dict:
    return {"visit_control_terms": ["Run-In", "Washout"]}
def create_activity_schedule(context: dict) -> dict:
    study = context.get("study", {})
    schedule = [{"schedule_id": "E1"}]
    return {"schedule": schedule}
def get_activity_schedule(context: dict) -> dict:
    study = context.get("study", {})
    schedule = [{"schedule_id": "E1"}]
    return {"schedule": schedule}
def create_design_cell(context: dict) -> dict:
    study = context.get("study", {})
    design_cell = [{"design_cell_id": "E1"}]
    return {"design_cell": design_cell}

# def create_branch_arms(context: dict) -> dict:
#     arms = context.get("arms", [])
#     branch_arms = [{"branch_arm_id": f"B_{a['arm_id']}"} for a in arms]
#     return {"branch_arms": branch_arms}

def create_element(context: dict) -> dict:
    study = context.get("study", {})
    elements = [{"element_id": "EL1"}]
    return {"elements": elements}

def fetch_arm_control_terminology(context: dict) -> dict:
    # e.g. GET terminology service
    return {"arm_control_terms": ["Control", "Placebo"]}

def fetch_epoch_control_terminology(context: dict) -> dict:
    return {"epoch_control_terms": ["Run-In", "Washout"]}

# def fetch_branch_arm_control_terminology(context: dict) -> dict:
#     return {"branch_arm_control_terms": ["Arm A Branch", "Arm B Branch"]}

def fetch_element_control_terminology(context: dict) -> dict:
    return {"element_control_terms": ["Lab", "Visit"]}


def fetch_activity_type_terminology(context: dict) -> dict:
    return {"epoch_control_terms": ["Run-In", "Washout"]}


def fetch_activity_group_control_terminology(context: dict) -> dict:
    return {"epoch_control_terms": ["Run-In", "Washout"]}


def fetch_activity_sub_group_control_terminology(context: dict) -> dict:
    return {"epoch_control_terms": ["Run-In", "Washout"]}


def fetch_soa_group_control_terminology(context: dict) -> dict:
    return {"epoch_control_terms": ["Run-In", "Washout"]}
