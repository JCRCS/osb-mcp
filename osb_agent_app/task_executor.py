# osb_agent_app/task_executor.py

import time
import requests
from requests.exceptions import HTTPError
from .task_steps import (
    create_study,
    create_study_arm,
    get_study_arms,
    preview_epoch,
    create_epoch,
    create_element,
    fetch_arm_control_terminology,
    fetch_epoch_control_terminology,
    fetch_element_control_terminology,
    fetch_activity_type_terminology,
    create_visit,
    preview_visit,
    fetch_time_point_reference_control_terminology,
    fetch_visit_control_terminology,
    get_study_visits,
    get_study_epochs,
    fetch_soa_group_control_terminology,
    fetch_study_activity,
    create_study_activity,
    create_activity_schedule,
    get_activity_schedule,
    create_design_cell


)

class TaskExecutor:
    """
    Executes atomic tasks sequentially. Each function accepts & returns a dict-like context.
    On HTTP errors, uses retry logic for 429 (rate-limit) or fails fast otherwise.
    """
    def __init__(self):
        self.steps = {
            "create_study": create_study,
            "get_study_arms": get_study_arms,
            "create_study_arm": create_study_arm,
            "create_visit":create_visit,
            "preview_visit":preview_visit,
            "fetch_time_point_reference_control_terminology":fetch_time_point_reference_control_terminology,
            "fetch_visit_control_terminology":fetch_visit_control_terminology,
            "get_study_visits":get_study_visits,
            "get_study_epochs":get_study_epochs,
            "preview_epoch": preview_epoch,
            "create_epoch": create_epoch,
            "create_study_activity": create_study_activity,
            "fetch_study_activity": fetch_study_activity,
            "create_element": create_element,
            "fetch_arm_control_terminology": fetch_arm_control_terminology,
            "fetch_epoch_control_terminology": fetch_epoch_control_terminology,
            "fetch_activity_type_terminology": fetch_activity_type_terminology,
            "fetch_soa_group_control_terminology": fetch_soa_group_control_terminology,
            "fetch_element_control_terminology": fetch_element_control_terminology,
            "create_design_cell":create_design_cell,
            "create_activity_schedule":create_activity_schedule,
            "get_activity_schedule":get_activity_schedule,
        }

    def execute(self, tasks: list[str]) -> list[dict]:
        context = {}
        results = []
        for t in tasks:
            fn = self.steps.get(t)
            if fn is None:
                results.append({"task": t, "status": "failed", "error": "NotImplemented"})
                break
            try:
                out = fn(context)
                # merge returned dict into context
                if isinstance(out, dict):
                    context.update(out)
                results.append({"task": t, "status": "success", "result": out})
            except HTTPError as http_err:
                status = http_err.response.status_code
                if status == 429:
                    retry_after = int(http_err.response.headers.get("Retry-After", 5))
                    time.sleep(retry_after)
                    # retry once
                    out = fn(context)
                    if isinstance(out, dict):
                        context.update(out)
                    results.append({"task": t, "status": "success", "result": out})
                else:
                    results.append({"task": t, "status": "failed", "error": str(http_err)})
                    break
            except Exception as e:
                results.append({"task": t, "status": "failed", "error": str(e)})
                break
        return results
