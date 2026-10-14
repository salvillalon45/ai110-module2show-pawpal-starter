"""PawPal+ logic layer: backend classes for tasks, pets, owners, and scheduling."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

TIME_BLOCKS = ("morning", "afternoon", "evening")

@dataclass
class Pet:
    name: str

@dataclass
class Task:
    name: str
    description: str
    duration: int  # minutes
    priority: int  # 1, 2, 3 (document which number means high)
    preferred_time: str  # one of TIME_BLOCKS
    completion_status: bool = False

@dataclass
class Owner:
    name: str
    pet: Optional[Pet] = None
    tasks: List[Task] = field(default_factory=list)
    # available minutes per time block, e.g. {"morning": 120, "afternoon": 0, "evening": 90}
    constraints: Dict[str, int] = field(default_factory=dict)

    def create_task(self, task: Task) -> None:
        pass

    def edit_task(self, task_name: str, **changes) -> None:
        pass

class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.plan: Dict[str, List[Task]] = {block: [] for block in TIME_BLOCKS}
        self.explanation_of_plan: str = ""
        self.skipped_tasks: Dict[str, str] = {}  # task name -> reason skipped

    def generate_daily_plan(self) -> None:
        pass

    def generate_explanation_of_plan(self) -> None:
        pass
