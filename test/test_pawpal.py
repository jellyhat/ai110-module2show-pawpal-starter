from pawpal_system import Pet, Task


def test_mark_complete_changes_task_status() -> None:
    task = Task(title="Give medication", duration_minutes=5, priority="high")

    assert task.is_complete is False

    task.mark_complete()

    assert task.is_complete is True


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="dog")
    task = Task(title="Morning walk", duration_minutes=20, priority="medium")

    assert len(pet.get_tasks()) == 0

    pet.add_task(task)

    assert len(pet.get_tasks()) == 1
    assert pet.get_tasks()[0] is task