from datetime import date, time

import pytest

from pawpal_system import Owner, Pet, ScheduledTask, Scheduler, Task


def test_mark_complete_changes_task_status() -> None:
    task = Task(title="Give medication", duration_minutes=5, priority="high")

    assert task.is_complete is False

    task.mark_complete()

    assert task.is_complete is True


def test_completing_daily_task_adds_next_day_occurrence() -> None:
    pet = Pet(name="Mochi", species="dog")
    task = Task(
        title="Medication",
        duration_minutes=5,
        priority="high",
        frequency="daily",
        due_time=time(8, 0),
        starts_on=date(2026, 10, 22),
    )
    pet.add_task(task)

    next_task = pet.complete_task(task, date(2026, 10, 23))

    assert task.is_complete is True
    assert task.completed_on == date(2026, 10, 23)
    assert next_task is not None
    assert next_task is not task
    assert next_task.title == task.title
    assert next_task.frequency == "daily"
    assert next_task.due_time == task.due_time
    assert next_task.is_complete is False
    assert next_task.starts_on == date(2026, 10, 24)
    assert pet.get_tasks() == [task, next_task]


def test_completing_weekly_task_adds_next_weekday_occurrence() -> None:
    pet = Pet(name="Mochi", species="dog")
    task = Task(
        title="Grooming",
        duration_minutes=20,
        priority="medium",
        frequency="weekly",
        starts_on=date(2026, 10, 23),
    )
    pet.add_task(task)

    next_task = pet.complete_task(task, date(2026, 10, 24))

    assert next_task is not None
    assert next_task.starts_on == date(2026, 10, 30)
    assert next_task.starts_on.weekday() == task.starts_on.weekday()
    assert next_task.is_complete is False


def test_completing_one_time_task_does_not_create_another() -> None:
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Nail trim", duration_minutes=15, priority="low")
    pet.add_task(task)

    next_task = pet.complete_task(task, date(2026, 10, 23))

    assert next_task is None
    assert task.is_complete is True
    assert pet.get_tasks() == [task]


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Morning walk", duration_minutes=20, priority="medium")

    assert len(pet.get_tasks()) == 0

    pet.add_task(task)

    assert len(pet.get_tasks()) == 1
    assert pet.get_tasks()[0] is task


def test_tasks_are_scheduled_by_due_time_then_priority() -> None:
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(
        Task(
            title="Later",
            duration_minutes=5,
            priority="high",
            due_time=time(9, 0),
        )
    )
    pet.add_task(
        Task(
            title="Earlier low priority",
            duration_minutes=5,
            priority="low",
            due_time=time(8, 30),
        )
    )
    pet.add_task(
        Task(
            title="Earlier high priority",
            duration_minutes=5,
            priority="high",
            due_time=time(8, 30),
        )
    )
    owner.add_pet(pet)

    plan = Scheduler().build_daily_plan(
        owner,
        available_minutes=30,
        day_start=time(8, 0),
        schedule_date=date(2026, 10, 23),
    )

    assert [entry.task.title for entry in plan.scheduled] == [
        "Earlier high priority",
        "Earlier low priority",
        "Later",
    ]


def test_sort_by_time_orders_tasks_and_places_missing_times_last() -> None:
    tasks = [
        Task(title="No due time", duration_minutes=5, priority="low"),
        Task(
            title="Evening",
            duration_minutes=5,
            priority="low",
            due_time=time(18, 0),
        ),
        Task(
            title="Morning",
            duration_minutes=5,
            priority="low",
            due_time=time(8, 30),
        ),
    ]

    sorted_tasks = Scheduler().sort_by_time(tasks)

    assert [task.title for task in sorted_tasks] == [
        "Morning",
        "Evening",
        "No due time",
    ]
    assert tasks[0].title == "No due time"


def test_sort_by_time_preserves_input_order_for_matching_times() -> None:
    tasks = [
        Task(
            title="First",
            duration_minutes=5,
            priority="medium",
            due_time=time(8, 0),
        ),
        Task(
            title="Second",
            duration_minutes=5,
            priority="medium",
            due_time=time(8, 0),
        ),
    ]

    assert Scheduler().sort_by_time(tasks) == tasks


def test_scheduler_filters_tasks_by_pet_and_completion_status() -> None:
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    completed = Task(title="Breakfast", duration_minutes=5, priority="high")
    completed.mark_complete(date(2026, 10, 23))
    mochi.add_task(completed)
    mochi.add_task(Task(title="Walk", duration_minutes=20, priority="medium"))
    luna = Pet(name="Luna", species="cat")
    luna.add_task(Task(title="Medication", duration_minutes=5, priority="high"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    filtered = Scheduler().filter_tasks(
        owner.get_all_tasks(),
        pet_name="mochi",
        status="pending",
        as_of_date=date(2026, 10, 23),
    )

    assert [
        (pet_task.pet.name, pet_task.task.title) for pet_task in filtered
    ] == [("Mochi", "Walk")]


def test_owner_task_filters_select_pet_and_status() -> None:
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    completed = Task(title="Breakfast", duration_minutes=5, priority="high")
    completed.mark_complete(date(2026, 10, 23))
    mochi.add_task(completed)
    mochi.add_task(Task(title="Walk", duration_minutes=20, priority="medium"))
    luna = Pet(name="Luna", species="cat")
    luna.add_task(Task(title="Medication", duration_minutes=5, priority="high"))
    owner.add_pet(mochi)
    owner.add_pet(luna)

    assert [
        item.task.title
        for item in owner.get_all_tasks(
            pet_name="mochi",
            status="pending",
            as_of_date=date(2026, 10, 23),
        )
    ] == ["Walk"]
    assert [
        item.task.title
        for item in owner.get_all_tasks(
            status="completed", as_of_date=date(2026, 10, 23)
        )
    ] == ["Breakfast"]


def test_daily_plan_can_filter_by_pet_and_status() -> None:
    owner = Owner(name="Jordan")
    mochi = Pet(name="Mochi", species="dog")
    mochi.add_task(Task(title="Walk", duration_minutes=20, priority="medium"))
    luna = Pet(name="Luna", species="cat")
    luna.add_task(
        Task(title="Medication", duration_minutes=5, priority="high")
    )
    owner.add_pet(mochi)
    owner.add_pet(luna)

    plan = Scheduler().build_daily_plan(
        owner,
        available_minutes=30,
        pet_name="Luna",
        status="pending",
        schedule_date=date(2026, 10, 23),
    )

    assert [entry.pet.name for entry in plan.scheduled] == ["Luna"]


def test_daily_recurring_task_returns_after_completion_day() -> None:
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    task = Task(
        title="Medication",
        duration_minutes=5,
        priority="high",
        frequency="daily",
    )
    pet.add_task(task)
    next_task = pet.complete_task(task, date(2026, 10, 22))
    owner.add_pet(pet)

    plan = Scheduler().build_daily_plan(
        owner,
        available_minutes=10,
        schedule_date=date(2026, 10, 23),
    )

    assert next_task is not None
    assert [entry.task for entry in plan.scheduled] == [next_task]


def test_completing_task_twice_does_not_create_duplicate_occurrences() -> None:
    pet = Pet(name="Mochi", species="dog")
    task = Task(
        title="Medication",
        duration_minutes=5,
        priority="high",
        frequency="daily",
    )
    pet.add_task(task)

    pet.complete_task(task, date(2026, 10, 23))
    tasks_after_first_completion = pet.get_tasks()

    with pytest.raises(ValueError, match="already complete"):
        pet.complete_task(task, date(2026, 10, 23))

    assert pet.get_tasks() == tasks_after_first_completion
    assert len(pet.get_tasks()) == 2


def test_weekly_recurring_task_only_appears_on_its_weekday() -> None:
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(
        Task(
            title="Weekly grooming",
            duration_minutes=20,
            priority="low",
            frequency="weekly",
            starts_on=date(2026, 10, 23),
        )
    )
    owner.add_pet(pet)
    scheduler = Scheduler()

    friday_plan = scheduler.build_daily_plan(
        owner, available_minutes=30, schedule_date=date(2026, 10, 23)
    )
    saturday_plan = scheduler.build_daily_plan(
        owner, available_minutes=30, schedule_date=date(2026, 10, 24)
    )

    assert len(friday_plan.scheduled) == 1
    assert not saturday_plan.scheduled
    assert "repeats weekly on Friday" in saturday_plan.skipped[0].reason


def test_deadline_conflict_is_reported() -> None:
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    pet.add_task(
        Task(
            title="Breakfast",
            duration_minutes=10,
            priority="high",
            due_time=time(8, 10),
        )
    )
    pet.add_task(
        Task(
            title="Medication",
            duration_minutes=10,
            priority="high",
            due_time=time(8, 15),
        )
    )
    owner.add_pet(pet)

    plan = Scheduler().build_daily_plan(
        owner,
        available_minutes=30,
        day_start=time(8, 0),
        schedule_date=date(2026, 10, 23),
    )

    assert [entry.task.title for entry in plan.scheduled] == ["Breakfast"]
    assert len(plan.skipped) == 1
    assert plan.skipped[0].task.title == "Medication"
    assert "Deadline conflict" in plan.skipped[0].reason


def test_task_finishing_exactly_at_deadline_is_scheduled() -> None:
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    task = Task(
        title="Breakfast",
        duration_minutes=10,
        priority="high",
        due_time=time(8, 10),
    )
    pet.add_task(task)
    owner.add_pet(pet)

    plan = Scheduler().build_daily_plan(
        owner,
        available_minutes=10,
        day_start=time(8, 0),
        schedule_date=date(2026, 10, 23),
    )

    assert [entry.task for entry in plan.scheduled] == [task]
    assert plan.skipped == []


def test_empty_pet_and_empty_task_lists_are_handled() -> None:
    owner = Owner(name="Jordan", pets=[Pet(name="Mochi", species="dog")])
    scheduler = Scheduler()
    empty_pet_tasks = owner.get_all_tasks()

    assert empty_pet_tasks == []
    assert scheduler.sort_by_time([]) == []
    assert scheduler.filter_tasks(empty_pet_tasks) == []

    plan = scheduler.build_daily_plan(
        owner,
        available_minutes=30,
        schedule_date=date(2026, 10, 23),
    )

    assert plan.scheduled == []
    assert plan.skipped == []


def test_insufficient_time_skips_task_without_partial_scheduling() -> None:
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Long walk", duration_minutes=20, priority="medium")
    pet.add_task(task)
    owner.add_pet(pet)

    plan = Scheduler().build_daily_plan(
        owner,
        available_minutes=0,
        schedule_date=date(2026, 10, 23),
    )

    assert plan.scheduled == []
    assert len(plan.skipped) == 1
    assert plan.skipped[0].task is task
    assert "only 0 minutes remain" in plan.skipped[0].reason


def test_detect_conflicts_warns_for_overlapping_tasks_across_pets() -> None:
    mochi = Pet(name="Mochi", species="dog")
    walk = Task(title="Walk", duration_minutes=25, priority="medium")
    mochi.add_task(walk)
    luna = Pet(name="Luna", species="cat")
    medication = Task(title="Medication", duration_minutes=5, priority="high")
    luna.add_task(medication)

    warnings = Scheduler().detect_conflicts(
        [
            ScheduledTask(mochi, walk, time(8, 0)),
            ScheduledTask(luna, medication, time(8, 10)),
        ]
    )

    assert len(warnings) == 1
    assert "Warning:" in warnings[0]
    assert "Walk for Mochi" in warnings[0]
    assert "Medication for Luna" in warnings[0]
    assert "08:10 to 08:15" in warnings[0]


def test_detect_conflicts_flags_tasks_with_identical_start_times() -> None:
    pet = Pet(name="Mochi", species="dog")
    breakfast = Task(title="Breakfast", duration_minutes=10, priority="high")
    medication = Task(title="Medication", duration_minutes=5, priority="high")
    pet.add_task(breakfast)
    pet.add_task(medication)

    warnings = Scheduler().detect_conflicts(
        [
            ScheduledTask(pet, breakfast, time(8, 0)),
            ScheduledTask(pet, medication, time(8, 0)),
        ]
    )

    assert len(warnings) == 1
    assert "Breakfast for Mochi" in warnings[0]
    assert "Medication for Mochi" in warnings[0]
    assert "08:00 to 08:05" in warnings[0]


def test_equal_due_times_do_not_conflict_when_scheduled_sequentially() -> None:
    pet = Pet(name="Mochi", species="dog")
    breakfast = Task(
        title="Breakfast",
        duration_minutes=5,
        priority="high",
        due_time=time(8, 30),
    )
    medication = Task(
        title="Medication",
        duration_minutes=5,
        priority="medium",
        due_time=time(8, 30),
    )
    pet.add_task(breakfast)
    pet.add_task(medication)
    scheduler = Scheduler()

    warnings = scheduler.detect_conflicts(
        [
            ScheduledTask(pet, breakfast, time(8, 0)),
            ScheduledTask(pet, medication, time(8, 5)),
        ]
    )

    assert warnings == []


def test_detect_conflicts_warns_for_same_pet_but_not_adjacent_tasks() -> None:
    pet = Pet(name="Mochi", species="dog")
    walk = Task(title="Walk", duration_minutes=25, priority="medium")
    medication = Task(title="Medication", duration_minutes=5, priority="high")
    pet.add_task(walk)
    pet.add_task(medication)
    scheduler = Scheduler()

    warnings = scheduler.detect_conflicts(
        [
            ScheduledTask(pet, walk, time(8, 0)),
            ScheduledTask(pet, medication, time(8, 20)),
        ]
    )
    adjacent_warnings = scheduler.detect_conflicts(
        [
            ScheduledTask(pet, walk, time(8, 0)),
            ScheduledTask(pet, medication, time(8, 25)),
        ]
    )

    assert len(warnings) == 1
    assert "08:20 to 08:25" in warnings[0]
    assert adjacent_warnings == []