# osb_agent_app/task_executor.py

import time
import requests
from requests.exceptions import HTTPError
from .task_steps import (
    create_study,
    create_study_arm,
    preview_epoch,
    create_epoch,
    # create_branch_arms,
    create_element,
    fetch_arm_control_terminology,
    fetch_epoch_control_terminology,
    # fetch_branch_arm_control_terminology,
    fetch_element_control_terminology,
)

class TaskExecutor:
    """
    Executes atomic tasks sequentially. Each function accepts & returns a dict-like context.
    On HTTP errors, uses retry logic for 429 (rate-limit) or fails fast otherwise.
    """
    def __init__(self):
        self.steps = {
            "create_study": create_study,
            "create_study_arm": create_study_arm,
            "preview_epoch": preview_epoch,
            "create_epoch": create_epoch,
            # "create_branch_arms": create_branch_arms,
            "create_element": create_element,
            "fetch_arm_control_terminology": fetch_arm_control_terminology,
            "fetch_epoch_control_terminology": fetch_epoch_control_terminology,
            # "fetch_branch_arm_control_terminology": fetch_branch_arm_control_terminology,
            "fetch_element_control_terminology": fetch_element_control_terminology,
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
