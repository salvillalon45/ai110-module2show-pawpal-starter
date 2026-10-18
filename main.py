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
