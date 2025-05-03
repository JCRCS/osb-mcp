# osb_agent_app/task_planner.py

from typing import List
from .planner_rules import PLANNER_RULES, TASK_DEPENDENCIES

class TaskPlanner:
    """
    Expands high-level goals into an ordered list of atomic tasks,
    resolving dependencies with a topological sort.
    """
    def plan(self, goals: List[str]) -> List[str]:
        ordered_goals: List[str] = []
        visited = set()

        def visit(g: str):
            if g in visited:
                return
            for dep in TASK_DEPENDENCIES.get(g, []):
                visit(dep)
            if g not in ordered_goals:
                ordered_goals.append(g)
            visited.add(g)

        for g in goals:
            if g not in PLANNER_RULES:
                raise ValueError(f"No rule defined for goal: {g}")
            visit(g)

        # Expand each goal into its atomic tasks
        tasks: List[str] = []
        for g in ordered_goals:
            tasks.extend(PLANNER_RULES[g])
        return tasks
