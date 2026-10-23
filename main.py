"""Run a small PawPal+ schedule demo in the terminal."""

from datetime import time

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="dog")
    mochi.add_task(
        Task(
            title="Breakfast",
            duration_minutes=10,
            priority="high",
            due_time=time(8, 0),
        )
    )
    mochi.add_task(
        Task(
            title="Morning walk",
            duration_minutes=25,
            priority="medium",
            due_time=time(9, 0),
        )
    )

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
    plan = scheduler.build_daily_plan(
        owner,
        available_minutes=60,
        day_start=time(7, 30),
    )

    print("Today's Schedule")
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()