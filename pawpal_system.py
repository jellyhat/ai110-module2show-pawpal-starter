"""Core class skeletons for the PawPal+ pet-care planner."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    """A care activity for a pet."""

    title: str
    duration_minutes: int
    priority: str
    frequency: str = "once"
    time: Optional[str] = None
    is_complete: bool = False

    def mark_complete(self) -> None:
        raise NotImplementedError


@dataclass
class Pet:
    """A pet and the care tasks associated with them."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def get_tasks(self) -> List[Task]:
        raise NotImplementedError


@dataclass
class Owner:
    """An owner who can manage multiple pets and their tasks."""

    name: str
    preferences: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def get_all_tasks(self) -> List[Task]:
        raise NotImplementedError


class Scheduler:
    """Coordinates tasks across all pets belonging to an owner."""

    def build_daily_plan(
        self, owner: Owner, available_minutes: int
    ) -> List[Task]:
        raise NotImplementedError

    def organize_tasks(
        self, tasks: List[Task], available_minutes: int
    ) -> List[Task]:
        raise NotImplementedError

    def explain_plan(self, plan: List[Task]) -> str:
        raise NotImplementedError