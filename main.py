"""Demonstrate sorting, filtering, and scheduling PawPal+ tasks in a terminal."""

from datetime import date, time

from pawpal_system import Owner, Pet, ScheduledTask, Scheduler, Task


def main() -> None:
    """Run the PawPal+ sorting, filtering, conflict, and schedule demo."""
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="dog")
    mochi.add_task(
        Task(
            title="Morning walk",
            duration_minutes=25,
            priority="medium",
            due_time=time(9, 0),
        )
    )
    mochi.add_task(
        Task(
            title="Breakfast",
            duration_minutes=10,
            priority="high",
            due_time=time(8, 0),
        )
    )
    completed_task = Task(
        title="Nail trim",
        duration_minutes=15,
        priority="low",
        due_time=time(12, 0),
    )
    mochi.add_task(completed_task)
    mochi.complete_task(completed_task, date.today())

    luna = Pet(name="Luna", species="cat")
    luna.add_task(
        Task(
            title="Medication",
            duration_minutes=5,
            priority="high",
            due_time=time(8, 30),
        )
    )

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler()
    pet_tasks = owner.get_all_tasks()
    print("Tasks sorted by due time:")
    for task in scheduler.sort_by_time(
        [pet_task.task for pet_task in pet_tasks]
    ):
        due_time = task.due_time.strftime("%H:%M") if task.due_time else "none"
        print(f"- {due_time} — {task.title}")

    print("\nPending tasks for Mochi:")
    for pet_task in scheduler.filter_tasks(
        pet_tasks,
        pet_name="Mochi",
        status="pending",
    ):
        print(f"- {pet_task.task.title}")

    print("\nCompleted tasks:")
    for pet_task in scheduler.filter_tasks(
        pet_tasks,
        status="completed",
        as_of_date=date.today(),
    ):
        print(f"- {pet_task.task.title} for {pet_task.pet.name}")

    overlapping_tasks = [
        ScheduledTask(pet=mochi, task=mochi.tasks[0], start_time=time(8, 0)),
        ScheduledTask(pet=luna, task=luna.tasks[0], start_time=time(8, 0)),
    ]
    print("\nConflict detection:")
    conflict_warnings = scheduler.detect_conflicts(overlapping_tasks)
    if conflict_warnings:
        for warning in conflict_warnings:
            print(warning)
    else:
        print("No scheduling conflicts found.")

    plan = scheduler.build_daily_plan(
        owner,
        available_minutes=60,
        day_start=time(7, 30),
    )

    print("\nToday's Schedule")
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()