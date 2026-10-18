from pawpal_system import Scheduler, Owner, Pet, Task, Priority, Frequency

# Sample data is chosen so every scheduler path shows up in the output:
#   - preferred block used        (meal prep fits in the morning)
#   - fallback to another block   (walks don't fit in the morning, move to evening)
#   - too long for any block      (bath 120 min and groom 150 min, longest block is 90)
#   - fits nowhere                (play fetch: morning and evening are nearly full)
#   - completed task ignored      (brush teeth)
#   - priority ordering           (HIGH tasks claim space before MEDIUM/LOW)

rex = Pet("Rex")
rex.create_task(
    Task(
        "walk", 
        "walk Rex in the local park nearby",
        30,
        Priority.HIGH,
        "morning",
        Frequency.DAILY
    )
)
rex.create_task(
    Task(
        "prep meal",
        "have the meal ready so I can just serve it",
        20,
        Priority.HIGH,
        "morning",
        Frequency.DAILY
    )
)
rex.create_task(
    Task(
        "bath",
        "give Rex a bath to maintain hygiene", 
        120,
        Priority.MEDIUM,
        "morning",
        Frequency.WEEKLY
    )
)
rex.create_task(
    Task(
        "play fetch", 
        "play fetch in the backyard",
        40,
        Priority.LOW,
        "morning",
        Frequency.DAILY
    )
)
rex.create_task(
    Task(
        "brush teeth",
        "brush Rex's teeth",
        10,
        Priority.LOW,
        "morning",
        Frequency.DAILY,
        completion_status=True
    )
)

buddy = Pet("Buddy")
buddy.create_task(
    Task(
        "walk",
        "walk Buddy in the local park nearby",
        30,
        Priority.HIGH,
        "morning",
        Frequency.DAILY
    )
)
buddy.create_task(
    Task(
        "prep meal",
        "have the meal ready so I can just serve it",
        20,
        Priority.HIGH,
        "morning",
        Frequency.DAILY
    )
)
buddy.create_task(
    Task(
        "nail trim",
        "trim Buddy's nails",
        15,
        Priority.MEDIUM,
        "morning",
        Frequency.WEEKLY
    )
)
buddy.create_task(
    Task(
        "full groom",
        "full grooming session",
        150,
        Priority.MEDIUM,
        "evening",
        Frequency.WEEKLY
    )
)

constraints = {
    "morning": 60,
    "afternoon": 0,
    "evening": 90,
}

jerry = Owner("Jerry", [rex, buddy], constraints)

scheduler = Scheduler(jerry)
scheduler.generate_daily_plan()
scheduler.generate_explanation_of_plan()

print(scheduler.explanation_of_plan)


# --- Sorting and filtering demo ---
# Tasks are added deliberately out of order (evening first, mixed priorities and
# durations) so the sorted output differs visibly from the insertion order.

def show(title, tasks):
    print(f"\n{title}")
    if not tasks:
        print("  (none)")
    for t in tasks:
        status = "done" if t.completion_status else "todo"
        print(
            f"  - [{status}] {t.pet_name}: {t.name} "
            f"({t.preferred_time}, {t.priority.name}, {t.duration} min)"
        )


whiskers = Pet("Whiskers", "cat")
whiskers.create_task(Task("play", "feather wand play", 15, Priority.LOW, "evening"))
whiskers.create_task(Task("litter box", "scoop litter", 10, Priority.MEDIUM, "afternoon"))
whiskers.create_task(Task("breakfast", "wet food", 5, Priority.HIGH, "morning"))
whiskers.create_task(Task("medicine", "ear drops", 5, Priority.HIGH, "evening"))
whiskers.create_task(Task("brush fur", "brush coat", 20, Priority.LOW, "morning"))
whiskers.create_task(Task("vet note", "write up vet notes", 10, Priority.LOW, "afternoon"))
whiskers.tasks[-1].mark_complete()

demo_owner = Owner("Sam", [whiskers, Pet("Mochi", "dog")], {"morning": 60, "afternoon": 30, "evening": 60})
demo_owner.pets[1].create_task(Task("evening walk", "walk Mochi", 30, Priority.HIGH, "evening"))
demo_owner.pets[1].create_task(Task("breakfast", "kibble", 5, Priority.HIGH, "morning"))
demo_owner.pets[1].tasks[0].mark_complete()

demo = Scheduler(demo_owner)

show("As added (unsorted):", demo_owner.get_all_tasks())
show("Sorted by time block, priority, duration (incomplete only):", demo.sort_by_time())
show("Filter: incomplete tasks", demo.filter_tasks(completed=False))
show("Filter: completed tasks", demo.filter_tasks(completed=True))
show("Filter: Whiskers' tasks", demo.filter_tasks(pet_name="Whiskers"))
show("Filter: Mochi's incomplete tasks", demo.filter_tasks(pet_name="Mochi", completed=False))
