# osb_agent_app/agent.py

from .goal_generator_llm import GoalGeneratorLLM
from .task_planner import TaskPlanner
from .task_executor import TaskExecutor

def run_llm_driven_workflow(user_request: str):
    """
    Orchestrates the full OSB workflow:
     1) LLM → high‑level goals
     2) Graph planner → ordered atomic tasks
     3) Executor → runs task_steps
    """
    # 1) Parse user into goals
    goal_gen = GoalGeneratorLLM()
    goals = goal_gen.generate_goals(user_request)

    # 2) Plan with dependencies
    planner = TaskPlanner()
    plan = planner.plan(goals)

    # 3) Execute tasks
    executor = TaskExecutor()
    return executor.execute(plan)

if __name__ == "__main__":
    import pprint
    out = run_llm_driven_workflow(
        "Create a study, add two arms and epochs, then fetch control terminology for arms and elements"
    )
    pprint.pprint(out)
