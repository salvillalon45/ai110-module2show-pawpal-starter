from pawpal_system import Task, Pet, Priority, Frequency


def make_task(name: str = "walk") -> Task:
    return Task(name, "a test task", 30, Priority.HIGH, "morning", Frequency.DAILY)


def test_mark_complete_changes_status():
    task = make_task()
    assert task.completion_status is False

    task.mark_complete()

    assert task.completion_status is True


def test_adding_task_increases_pet_task_count():
    pet = Pet("Rex")
    assert len(pet.tasks) == 0

    pet.create_task(make_task("walk"))
    assert len(pet.tasks) == 1

    pet.create_task(make_task("feed"))
    assert len(pet.tasks) == 2
