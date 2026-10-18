"""PawPal+ logic layer: backend classes for tasks, pets, owners, and scheduling."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from enum import Enum, IntEnum
from typing import Dict, List, Optional, Tuple

TIME_BLOCKS = ("morning", "afternoon", "evening")


class Priority(IntEnum):
    """Lower number = more important."""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class Frequency(str, Enum):
    """How often a task recurs."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    name: str
    description: str
    duration: int  # minutes, must be > 0
    priority: Priority  # Priority.HIGH (1) is scheduled first
    preferred_time: str  # one of TIME_BLOCKS; soft preference, scheduler may fall back
    frequency: Frequency = Frequency.DAILY
    completion_status: bool = False
    pet_name: str = ""  # set by Pet.create_task; don't pass it yourself
    due_date: date = field(default_factory=date.today)  # day this task is due; defaults to today

    def __post_init__(self) -> None:
        """Validate duration and preferred_time, and coerce priority and frequency to enums."""
        if self.duration <= 0:
            raise ValueError(f"duration must be > 0, got {self.duration}")
        if self.preferred_time not in TIME_BLOCKS:
            raise ValueError(
                f"preferred_time must be one of {TIME_BLOCKS}, got {self.preferred_time!r}"
            )
        self.priority = Priority(self.priority)
        self.frequency = Frequency(self.frequency)

    def mark_complete(self) -> None:
        """Mark this task as done so the scheduler skips it."""
        self.completion_status = True

    def next_occurrence(self) -> Optional["Task"]:
        """Return an incomplete copy due on the next occurrence, or None for ONCE tasks.

        Daily tasks move forward 1 day and weekly tasks 7 days, counted from this
        task's due_date (not today), so finishing a task late doesn't skip a day.
        """
        if self.frequency == Frequency.DAILY:
            step = timedelta(days=1)
        elif self.frequency == Frequency.WEEKLY:
            step = timedelta(weeks=1)
        else:
            return None
        # pet_name is cleared so Pet.create_task can attach the copy
        return replace(
            self, completion_status=False, pet_name="", due_date=self.due_date + step
        )


@dataclass
class Pet:
    name: str
    species: str = "other"  # e.g. "dog", "cat", "other"
    tasks: List[Task] = field(default_factory=list)

    def create_task(self, task: Task) -> None:
        """Attach a task to this pet. Incomplete task names must be unique per pet.

        Completed tasks are kept as history, so a new task may reuse their name
        (this is how recurring tasks get their next occurrence).
        """
        if task.pet_name:
            raise ValueError(f"task {task.name!r} already belongs to {task.pet_name!r}")
        if any(t.name == task.name and not t.completion_status for t in self.tasks):
            raise ValueError(f"{self.name} already has a task named {task.name!r}")
        task.pet_name = self.name
        self.tasks.append(task)

    def complete_task(self, task_name: str) -> Optional[Task]:
        """Mark the named task complete and, if it recurs, add its next occurrence.

        Targets the pet's incomplete task with that name, so completing "walk" twice
        completes today's walk and then the next day's. Returns the newly created
        task, or None if the task doesn't recur or only completed copies remain.
        """
        task = self._find_task(task_name)
        if task.completion_status:
            return None
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            self.create_task(next_task)
        return next_task

    def edit_task(self, task_name: str, **changes) -> None:
        """Update fields on the task with the given name."""
        if "pet_name" in changes:
            raise ValueError("pet_name is set by create_task and can't be edited")
        task = self._find_task(task_name)
        for key, value in changes.items():
            if not hasattr(task, key):
                raise AttributeError(f"Task has no field {key!r}")
            setattr(task, key, value)
        task.__post_init__()  # re-validate

    def remove_task(self, task_name: str) -> None:
        """Delete the task with the given name from this pet."""
        self.tasks.remove(self._find_task(task_name))

    def _find_task(self, task_name: str) -> Task:
        """Return the task with the given name, or raise KeyError if there isn't one.

        Prefers the incomplete task when a completed one shares the name.
        """
        matches = [t for t in self.tasks if t.name == task_name]
        if not matches:
            raise KeyError(f"no task named {task_name!r}")
        for task in matches:
            if not task.completion_status:
                return task
        return matches[0]


@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)
    # available minutes per time block, e.g. {"morning": 120, "afternoon": 0, "evening": 90}
    constraints: Dict[str, int] = field(
        default_factory=lambda: {block: 0 for block in TIME_BLOCKS}
    )

    def __post_init__(self) -> None:
        """Reject unknown time blocks and default any missing blocks to 0 minutes."""
        unknown =set(self.constraints) - set(TIME_BLOCKS)
        if unknown:
            raise ValueError(f"unknown time blocks in constraints: {sorted(unknown)}")
        # blocks the caller left out have no available time
        for block in TIME_BLOCKS:
            self.constraints.setdefault(block, 0)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner; pet names must be unique."""
        if any(p.name == pet.name for p in self.pets):
            raise ValueError(f"a pet named {pet.name!r} already exists")
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Every task across all of the owner's pets."""
        result = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append(task)
        return result

class Scheduler:
    def __init__(self, owner: Owner):
        """Create a scheduler for the given owner with an empty plan."""
        self.owner = owner
        self.plan: Dict[str, List[Task]] = {block: [] for block in TIME_BLOCKS}
        self.explanation_of_plan: str = ""
        self.skipped_tasks: Dict[Tuple[str, str], str] = {}  # (pet, task) -> reason skipped
        self.placement_reasons: Dict[Tuple[str, str], str] = {}  # (pet, task) -> why it went where it did

    def sort_by_time(self) -> List[Task]:
        """
        Return incomplete tasks ordered by preferred time block, then highest priority
        then shortest duration first.

        Ties break on priority (HIGH first). Doesn't modify the plan or any task.
        """
        tasks = []
        for t in self.owner.get_all_tasks():
            if not t.completion_status:
                tasks.append(t)
        tasks.sort(
            key=lambda t: (TIME_BLOCKS.index(t.preferred_time), t.priority, t.duration)
        )
        return tasks

    def mark_task_complete(self, pet_name: str, task_name: str) -> Optional[Task]:
        """Complete a pet's task; recurring tasks get their next occurrence automatically.

        Returns the newly created task (or None). Raises KeyError for an unknown pet or task.
        """
        for pet in self.owner.pets:
            if pet.name == pet_name:
                return pet.complete_task(task_name)
        raise KeyError(f"no pet named {pet_name!r}")

    def filter_tasks(
        self, pet_name: Optional[str] = None, completed: Optional[bool] = None
    ) -> List[Task]:
        """Return the owner's tasks matching the given filters.

        pet_name: only tasks belonging to that pet (None = all pets).
        completed: True = only finished tasks, False = only unfinished tasks
            (None = both). Filters combine, so both can be given at once.
        """
        tasks = []
        for t in self.owner.get_all_tasks():
            if pet_name is not None and t.pet_name != pet_name:
                continue
            if completed is not None and t.completion_status != completed:
                continue
            tasks.append(t)
        return tasks

    def generate_daily_plan(self) -> None:
        """Build self.plan from the owner's incomplete tasks.

        Intended approach:
        - Reset plan, skipped_tasks and placement_reasons first (safe to re-run).
        - Work from a copy of owner.constraints; never mutate the owner's data.
        - Sort incomplete tasks by priority, then duration.
        - Try preferred_time first, then fall back to other blocks.
        - Skip (with a reason) tasks longer than every block or that fit nowhere.
        """
        self.plan = {block: [] for block in TIME_BLOCKS}
        self.skipped_tasks = {}
        self.placement_reasons = {}

        remaining = dict(self.owner.constraints)  # copy; owner's data stays untouched
        longest_block = max(remaining.values(), default=0)

        tasks = []
        for t in self.owner.get_all_tasks():
            if not t.completion_status:
                tasks.append(t)
        tasks.sort(key=lambda t: (t.priority, t.duration))

        for task in tasks:
            key = (task.pet_name, task.name)

            if task.duration > longest_block:
                self.skipped_tasks[key] = (
                    f"{task.duration} min is longer than any available time block "
                    f"(longest is {longest_block} min)"
                )
                continue

            # preferred block first, then the others in their normal order
            order = [task.preferred_time] + [
                b for b in TIME_BLOCKS if b != task.preferred_time
            ]
            for block in order:
                if task.duration <= remaining[block]:
                    self.plan[block].append(task)
                    remaining[block] -= task.duration
                    if block == task.preferred_time:
                        self.placement_reasons[key] = (
                            f"placed in preferred block '{block}' "
                            f"({task.priority.name} priority)"
                        )
                    else:
                        self.placement_reasons[key] = (
                            f"preferred '{task.preferred_time}' was full; "
                            f"moved to '{block}' ({task.priority.name} priority)"
                        )
                    break
            else:
                self.skipped_tasks[key] = (
                    f"no block has {task.duration} min left "
                    f"(remaining: {remaining})"
                )

    def generate_explanation_of_plan(self) -> None:
        """Format placement_reasons and skipped_tasks into explanation_of_plan."""
        lines = []

        for block in TIME_BLOCKS:
            tasks = self.plan[block]
            used = sum(t.duration for t in tasks)
            available = self.owner.constraints[block]
            lines.append(f"{block.capitalize()} ({used}/{available} min used):")
            if not tasks:
                lines.append("  (nothing scheduled)")
            for task in tasks:
                reason = self.placement_reasons[(task.pet_name, task.name)]
                lines.append(
                    f"  - {task.pet_name}: {task.name} ({task.duration} min) - {reason}"
                )

        if self.skipped_tasks:
            lines.append("")
            lines.append("Skipped:")
            for (pet_name, task_name), reason in self.skipped_tasks.items():
                lines.append(f"  - {pet_name}: {task_name} - {reason}")

        self.explanation_of_plan = "\n".join(lines)
