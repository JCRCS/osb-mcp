# osb_agent_app/task_steps.py

def create_study(context: dict) -> dict:
    # e.g. POST /studies
    study = {"study_id": "STU123"}
    return {"study": study}

def create_study_arms(context: dict) -> dict:
    study = context.get("study", {})
    # e.g. POST /studies/{id}/arms
    arms = [{"arm_id": "ARM1"}, {"arm_id": "ARM2"}]
    return {"arms": arms}

def create_epochs(context: dict) -> dict:
    study = context.get("study", {})
    epochs = [{"epoch_id": "E1"}]
    return {"epochs": epochs}

def create_branch_arms(context: dict) -> dict:
    arms = context.get("arms", [])
    branch_arms = [{"branch_arm_id": f"B_{a['arm_id']}"} for a in arms]
    return {"branch_arms": branch_arms}

def create_elements(context: dict) -> dict:
    study = context.get("study", {})
    elements = [{"element_id": "EL1"}]
    return {"elements": elements}

def fetch_arm_control_terminology(context: dict) -> dict:
    # e.g. GET terminology service
    return {"arm_control_terms": ["Control", "Placebo"]}

def fetch_epoch_control_terminology(context: dict) -> dict:
    return {"epoch_control_terms": ["Run-In", "Washout"]}

def fetch_branch_arm_control_terminology(context: dict) -> dict:
    return {"branch_arm_control_terms": ["Arm A Branch", "Arm B Branch"]}

def fetch_element_control_terminology(context: dict) -> dict:
    return {"element_control_terms": ["Lab", "Visit"]}
