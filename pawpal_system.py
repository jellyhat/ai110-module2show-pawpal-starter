"""Core models and scheduling logic for the PawPal+ pet-care planner."""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import List, Optional


@dataclass
class Task:
    """A care activity for a pet."""

    title: str
    duration_minutes: int
    priority: str
    frequency: str = "once"
    due_time: Optional[time] = None
    is_complete: bool = False
    starts_on: date = field(default_factory=date.today)
    completed_on: Optional[date] = None

    def __post_init__(self) -> None:
        """Validate the task's required fields."""
        if not self.title.strip():
            raise ValueError("title cannot be empty")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be greater than zero")
        if self.priority not in {"low", "medium", "high"}:
            raise ValueError("priority must be 'low', 'medium', or 'high'")
        if self.frequency not in {"once", "daily", "weekly"}:
            raise ValueError("frequency must be 'once', 'daily', or 'weekly'")

    def mark_complete(self, completed_on: Optional[date] = None) -> None:
        """Mark this task or its current recurring occurrence complete."""
        self.is_complete = True
        self.completed_on = completed_on or date.today()


def _is_complete_on(task: Task, schedule_date: date) -> bool:
    """Return whether this task occurrence was complete by the given date."""
    return task.is_complete and (
        task.completed_on is None or task.completed_on <= schedule_date
    )


def _avoid_terms(preferences: List[str]) -> List[str]:
    """Extract normalized terms from owner avoid preferences."""
    terms = []
    for preference in preferences:
        if not isinstance(preference, str):
            raise TypeError("preferences must contain only strings")
        prefix, separator, value = preference.partition(":")
        if not separator or prefix.strip().casefold() != "avoid":
            raise ValueError(
                "preferences must use the format 'avoid: <task title term>'"
            )
        term = value.strip().casefold()
        if not term:
            raise ValueError("avoid preferences must include a term")
        terms.append(term)
    return terms


@dataclass
class Pet:
    """A pet and the care tasks associated with them."""

    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the pet's identity and initial tasks."""
        if not self.name.strip():
            raise ValueError("name cannot be empty")
        if not self.species.strip():
            raise ValueError("species cannot be empty")
        if any(not isinstance(task, Task) for task in self.tasks):
            raise TypeError("tasks must contain only Task instances")

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        if not isinstance(task, Task):
            raise TypeError("task must be a Task")
        self.tasks.append(task)

    def complete_task(
        self,
        task: Task,
        completed_on: Optional[date] = None,
    ) -> Optional[Task]:
        """Complete a task and add its next occurrence when it recurs."""
        if not isinstance(task, Task):
            raise TypeError("task must be a Task")
        if not any(existing is task for existing in self.tasks):
            raise ValueError("task does not belong to this pet")
        if task.is_complete:
            raise ValueError("task is already complete")

        completion_date = completed_on or date.today()
        task.mark_complete(completion_date)
        if task.frequency == "once":
            return None

        if task.frequency == "daily":
            next_date = completion_date + timedelta(days=1)
        else:
            days_until_weekday = (
                task.starts_on.weekday() - completion_date.weekday()
            ) % 7
            next_date = completion_date + timedelta(
                days=days_until_weekday or 7
            )

        next_task = Task(
            title=task.title,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            frequency=task.frequency,
            due_time=task.due_time,
            starts_on=next_date,
        )
        self.add_task(next_task)
        return next_task

    def get_tasks(self) -> List[Task]:
        """Return a copy of this pet's care tasks."""
        return list(self.tasks)


@dataclass
class Owner:
    """An owner who can manage multiple pets and their tasks."""

    name: str
    preferences: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the owner's identity, preferences, and pets."""
        if not self.name.strip():
            raise ValueError("name cannot be empty")
        _avoid_terms(self.preferences)
        if any(not isinstance(pet, Pet) for pet in self.pets):
            raise TypeError("pets must contain only Pet instances")
        if len({id(pet) for pet in self.pets}) != len(self.pets):
            raise ValueError("an owner cannot register the same pet more than once")

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        if not isinstance(pet, Pet):
            raise TypeError("pet must be a Pet")
        if any(existing is pet for existing in self.pets):
            raise ValueError(f"{pet.name} is already registered to this owner")
        self.pets.append(pet)

    def get_all_tasks(
        self,
        pet_name: Optional[str] = None,
        status: str = "all",
        as_of_date: Optional[date] = None,
    ) -> List["PetTask"]:
        """Return task-pet pairs filtered by pet name and completion status."""
        if status not in {"all", "pending", "completed"}:
            raise ValueError("status must be 'all', 'pending', or 'completed'")
        if pet_name is not None and not pet_name.strip():
            raise ValueError("pet_name cannot be empty")

        schedule_date = as_of_date or date.today()
        pet_name_key = pet_name.casefold() if pet_name is not None else None
        matching_tasks = [
            PetTask(pet=pet, task=task)
            for pet in self.pets
            for task in pet.get_tasks()
            if pet_name_key is None or pet.name.casefold() == pet_name_key
        ]
        if status == "all":
            return matching_tasks
        return [
            pet_task
            for pet_task in matching_tasks
            if _is_complete_on(pet_task.task, schedule_date)
            == (status == "completed")
        ]


@dataclass
class PetTask:
    """A task together with the pet it belongs to."""

    pet: Pet
    task: Task


@dataclass
class ScheduledTask:
    """A task assigned a start time in a daily plan."""

    pet: Pet
    task: Task
    start_time: time


@dataclass
class SkippedTask:
    """A task omitted from a plan, with the reason it was skipped."""

    pet: Pet
    task: Task
    reason: str


@dataclass
class SchedulePlan:
    """Scheduled and skipped tasks for one available-time budget."""

    scheduled: List[ScheduledTask] = field(default_factory=list)
    skipped: List[SkippedTask] = field(default_factory=list)
    available_minutes: int = 0
    day_start: time = time(8, 0)


class Scheduler:
    """Coordinates tasks across all pets belonging to an owner."""

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted by due time, with unscheduled times last."""
        if any(not isinstance(task, Task) for task in tasks):
            raise TypeError("tasks must contain only Task instances")
        return sorted(
            tasks,
            key=lambda task: (
                task.due_time is None,
                task.due_time or time.max,
            ),
        )

    def filter_tasks(
        self,
        pet_tasks: List[PetTask],
        pet_name: Optional[str] = None,
        status: str = "all",
        as_of_date: Optional[date] = None,
    ) -> List[PetTask]:
        """Filter pet-task pairs by pet name and completion status."""
        if status not in {"all", "pending", "completed"}:
            raise ValueError("status must be 'all', 'pending', or 'completed'")
        if pet_name is not None and not pet_name.strip():
            raise ValueError("pet_name cannot be empty")
        if any(not isinstance(pet_task, PetTask) for pet_task in pet_tasks):
            raise TypeError("pet_tasks must contain only PetTask instances")

        schedule_date = as_of_date or date.today()
        pet_name_key = pet_name.casefold() if pet_name is not None else None
        return [
            pet_task
            for pet_task in pet_tasks
            if (
                pet_name_key is None
                or pet_task.pet.name.casefold() == pet_name_key
            )
            and (
                status == "all"
                or _is_complete_on(pet_task.task, schedule_date)
                == (status == "completed")
            )
        ]

    def detect_conflicts(
        self,
        scheduled_tasks: List[ScheduledTask],
    ) -> List[str]:
        """Return warnings for scheduled tasks whose time intervals overlap."""
        if any(
            not isinstance(entry, ScheduledTask) for entry in scheduled_tasks
        ):
            raise TypeError(
                "scheduled_tasks must contain only ScheduledTask instances"
            )

        warnings = []
        for index, first in enumerate(scheduled_tasks):
            first_start = (
                first.start_time.hour * 60
                + first.start_time.minute
                + first.start_time.second / 60
            )
            first_end = first_start + first.task.duration_minutes
            for second in scheduled_tasks[index + 1 :]:
                second_start = (
                    second.start_time.hour * 60
                    + second.start_time.minute
                    + second.start_time.second / 60
                )
                second_end = second_start + second.task.duration_minutes
                overlap_start = max(first_start, second_start)
                overlap_end = min(first_end, second_end)
                if overlap_start < overlap_end:
                    overlap_start_time = time(
                        int(overlap_start // 60) % 24,
                        int(overlap_start % 60),
                    )
                    overlap_end_time = time(
                        int(overlap_end // 60) % 24,
                        int(overlap_end % 60),
                    )
                    warnings.append(
                        f"Warning: {first.task.title} for {first.pet.name} "
                        f"overlaps {second.task.title} for {second.pet.name} "
                        f"from {overlap_start_time:%H:%M} to "
                        f"{overlap_end_time:%H:%M}."
                    )
        return warnings

    def build_daily_plan(
        self,
        owner: Owner,
        available_minutes: int,
        day_start: time = time(8, 0),
        pet_name: Optional[str] = None,
        status: str = "all",
        schedule_date: Optional[date] = None,
    ) -> SchedulePlan:
        """Build a daily plan from all tasks belonging to the owner."""
        plan_date = schedule_date or date.today()
        return self.organize_tasks(
            owner.get_all_tasks(),
            available_minutes,
            day_start,
            preferences=owner.preferences,
            pet_name=pet_name,
            status=status,
            schedule_date=plan_date,
        )

    def organize_tasks(
        self,
        pet_tasks: List[PetTask],
        available_minutes: int,
        day_start: time = time(8, 0),
        preferences: Optional[List[str]] = None,
        pet_name: Optional[str] = None,
        status: str = "all",
        schedule_date: Optional[date] = None,
    ) -> SchedulePlan:
        """Order tasks and record scheduled and skipped entries."""
        if available_minutes < 0:
            raise ValueError("available_minutes cannot be negative")
        if status not in {"all", "pending", "completed"}:
            raise ValueError("status must be 'all', 'pending', or 'completed'")
        if pet_name is not None and not pet_name.strip():
            raise ValueError("pet_name cannot be empty")

        avoid_terms = _avoid_terms(preferences or [])
        priority_rank = {"high": 0, "medium": 1, "low": 2}
        plan_date = schedule_date or date.today()
        pet_name_key = pet_name.casefold() if pet_name is not None else None
        plan = SchedulePlan(
            available_minutes=available_minutes,
            day_start=day_start,
        )
        eligible_tasks = []
        for index, pet_task in enumerate(pet_tasks):
            if not isinstance(pet_task, PetTask):
                raise TypeError("pet_tasks must contain only PetTask instances")

            task = pet_task.task
            if pet_name_key is not None and pet_task.pet.name.casefold() != pet_name_key:
                continue

            task_is_complete = _is_complete_on(task, plan_date)
            if status == "pending" and task_is_complete:
                continue
            if status == "completed" and not task_is_complete:
                continue

            if task.frequency != "once" and plan_date < task.starts_on:
                plan.skipped.append(
                    SkippedTask(
                        pet_task.pet,
                        task,
                        f"Recurrence starts on {task.starts_on:%Y-%m-%d}.",
                    )
                )
                continue

            if task.frequency == "weekly" and (
                plan_date.weekday() != task.starts_on.weekday()
            ):
                plan.skipped.append(
                    SkippedTask(
                        pet_task.pet,
                        task,
                        (
                            "Not due today; this task repeats weekly on "
                            f"{task.starts_on:%A}."
                        ),
                    )
                )
                continue

            if task_is_complete:
                plan.skipped.append(
                    SkippedTask(pet_task.pet, task, "Already completed.")
                )
                continue

            matching_avoid_term = next(
                (
                    term
                    for term in avoid_terms
                    if term in task.title.casefold()
                ),
                None,
            )
            if matching_avoid_term is not None:
                plan.skipped.append(
                    SkippedTask(
                        pet_task.pet,
                        task,
                        (
                            "Excluded by owner preference "
                            f"'avoid: {matching_avoid_term}'."
                        ),
                    )
                )
                continue

            eligible_tasks.append((index, pet_task))

        ordered_tasks = sorted(
            eligible_tasks,
            key=lambda item: (
                item[1].task.due_time is None,
                item[1].task.due_time or time.max,
                priority_rank[item[1].task.priority],
                item[0],
            ),
        )

        remaining_minutes = available_minutes
        current_time = datetime.combine(plan_date, day_start)
        end_of_day = datetime.combine(plan_date + timedelta(days=1), time.min)

        for _, pet_task in ordered_tasks:
            task = pet_task.task
            if task.duration_minutes > remaining_minutes:
                plan.skipped.append(
                    SkippedTask(
                        pet=pet_task.pet,
                        task=task,
                        reason=(
                            f"Needs {task.duration_minutes} minutes, but only "
                            f"{remaining_minutes} minutes remain."
                        ),
                    )
                )
                continue

            finish_time = current_time + timedelta(
                minutes=task.duration_minutes
            )
            if finish_time > end_of_day:
                plan.skipped.append(
                    SkippedTask(
                        pet=pet_task.pet,
                        task=task,
                        reason="Would extend beyond the end of the day.",
                    )
                )
                continue

            if task.due_time is not None:
                deadline = datetime.combine(plan_date, task.due_time)
                if finish_time > deadline:
                    conflict_detail = (
                        f"Deadline conflict: starting at "
                        f"{current_time:%H:%M} would finish at "
                        f"{finish_time:%H:%M}, after its "
                        f"{task.due_time:%H:%M} due time."
                    )
                    plan.skipped.append(
                        SkippedTask(
                            pet=pet_task.pet,
                            task=task,
                            reason=conflict_detail,
                        )
                    )
                    continue

            plan.scheduled.append(
                ScheduledTask(
                    pet=pet_task.pet,
                    task=task,
                    start_time=current_time.time(),
                )
            )
            current_time = finish_time
            remaining_minutes -= task.duration_minutes

        return plan

    def explain_plan(self, plan: SchedulePlan) -> str:
        """Format a readable summary of scheduled and skipped tasks."""
        lines = [
            f"Daily plan starting at {plan.day_start:%H:%M} "
            f"({plan.available_minutes} minutes available). "
            "Tasks are ordered by due time, then priority:"
        ]
        if plan.scheduled:
            for entry in plan.scheduled:
                lines.append(
                    f"- {entry.start_time:%H:%M} — {entry.task.title} "
                    f"for {entry.pet.name} "
                    f"({entry.task.duration_minutes} min, "
                    f"{entry.task.priority} priority)"
                )
        else:
            lines.append("- No tasks scheduled.")

        for entry in plan.skipped:
            lines.append(
                f"- Not scheduled: {entry.task.title} for {entry.pet.name} "
                f"({entry.reason})"
            )
        return "\n".join(lines)