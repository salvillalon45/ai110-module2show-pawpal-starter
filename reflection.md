# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The core actions a user can take in natural language:
- A user can add their owner and pet info and track care tasks (walks, feeding, meds, enrichment, grooming, etc.), including adding and editing them.
- A user can enter their constraints and priorities, such as available time, priority in their tasks, and owner preferences to guide the daily plan.
- A user can view a daily plan based on their constraints and priorities. They will understand why this plan was created for them.

**b. UML and Classes**
- Briefly describe your initial UML design.

The UML design has four classes Owner, Pet, Task, and Scheduler. It has the following relationships 
```
Owner "1" --> "1" Pet : has
Owner "1" --> "*" Task : has
Scheduler "1" --> "1" Owner : reads from
```
The UML shows that Pet and Task class are use as dataclasses. They have no methods. The Owner and Scheduler use those dataclasses for their own logic.
- What classes did you include, and what responsibilities did you assign to each?
I included the following classes Owner, Pet, Task, and Scheduler. 
### Pet
is a dataclass that just contains the name of the pet. 

### Task
is another dataclass that has attributes related to filling out the task for pet care. 

### Owner
is a class that represents the owner user in the app. **The relationships** that it has are:
- Owner has one Pet
- Owner has more than one Task. 

**tasks** is a list of Task objects that the Owner has created.

**constraints** is a dictionary that describes how much time the owner has available in each part of the day, so that the scheduler can decide which pet tasks fit where. constraints is the input (the time available). Example of how it will look like:
```
owner = Owner(
    name="Sal",
    constraints={"morning": 120, "afternoon": 0, "evening": 90},
)
```

**createTask()** allows the Owner to create a task.

**editTask()** allows the Owner to edit a task.

### Scheduler
is a class that represent the system that creates the daily plan for the Owner.
**The relationships** that it has are:
- Scheduler reads from an Owner

**owner** has access to the owner object.

**plan** is the Scheduler's output. This is how the structure will look like: 
```
plan = {
    "morning":   [Task("Walk Buddy", 45), Task("Groom Buddy", 60), Task("Feed Buddy", 10)],
    "afternoon": [],
    "evening":   [Task("Give meds", 5)],
}
```

**explanationOfPlan** an explanation of the plan given to the Owner to explain why the plan was created this way.

**skippedTasks** a dictionary containing the tasks it could not fit in the plan due to scheduling conflicts. It will store the title of the skipped task as the key

**generateDailyPlan()** the method in charge of generating the plan output

**generateExplanationOfPlan()** the method in charge of generating the explanation of the plan

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I ask the LLM and these are the changes we came up with.
**Constraints:**
- `constraints` now defaults to 0 minutes for every block in TIME_BLOCKS.
- Blocks you leave out are filled with 0.
- Unknown block names, like "mornin", raise a ValueError.
- This is needed so that constraints is only filled with keys we actually use. It will defend against typos.

**Pets and tasks:**
- `Owner.pet` is now `Owner.pets: List[Pet]`. This is needed to address more than on pet for an owner.
- Task has an optional pet_name field, so each task can be tied to a pet.

**Task validation:**
- `Task.__post_init__` rejects a duration of 0 or less and a `preferred_time` that is not in TIME_BLOCKS.
- `priority` is now a `Priority` enum (HIGH=1, MEDIUM=2, LOW=3). Plain ints like `1` still work. This is to standardize the priority intake.

**Owner methods:**
- `create_task` creates new tasks and enforces unique task names.
- `edit_task` edits the task. After the function finishes editing the tasks it re-validates by calling `Task.__post_init__` to make sure that the task is valid.
- `remove_task` is new.

**Scheduler:**
Added a `placement_reasons` dict, so `generate_explanation_of_plan` can format reasons recorded during scheduling. The docstring on `generate_daily_plan` spells out the intended approach.

**Also made the following new updates to the UML diagram:**
- Owner "1" --> "*" Pet
- `pet_name` added to `Task`
- `remove_task` added to `Owner`
- `placement_reasons` added to `Scheduler`

### After starting Phase 2: Core Implementation
Once I started this phase, the assigment suggested some edits that we should. I had to redo my UML diagram and also move my logic in my classes to fit what the assigment suggested. I did the following:
**Pet Class Changes**
- Pet class now has the methods create_task, edit_task, remove_task, _find_task. Pet class also has a list of tasks. This is needed because now a Pet has tasks.
**Task Class Changes**
- Task class is now linked to a Pet by the pet_name attribute
- Task class now has a frequency enum field
**Owner Class Changes**
- Owner class now has a method called get_all_tasks that gets all the tasks from all the owners pets
- Owner class now has a method called add_pet. It adds a pet to the list of pets an owner has

**The relationships between the Classes has changed**
- Pet "1" --> "*" Task : has
    - A Pet has more than one Task
- Task --> Priority
    - A Task a has Priority Enum
- Task --> Frequency
    - A Task a has Frequency Enum
- Owner "1" --> "*" Pet : has
    - An Owner has more than one Pet
- Scheduler "1" --> "1" Owner : reads from
    - A Scheduler reads from one Owner

**c. More updates to the design**

This section is the history of how the UML changed after the first design, in the order the changes happened.

**Phase 4: Algorithmic Layer**
- **Sorting.** `Scheduler.sort_by_time()` orders tasks by time block (morning, afternoon, evening), then priority, then shortest duration. I kept `duration` in minutes instead of switching to HH:MM, because the assignment's HH:MM idea is about a clock time, which `duration` is not. Later I changed it to also sort by `start_time` within a block, and to take an optional list of tasks so it can sort the output of `filter_tasks`.
- **Filtering.** `Scheduler.filter_tasks(pet_name, completed)` is one method with two optional filters, so they can be combined, for example "Tom's unfinished tasks". `completed=True` returns finished tasks, `False` returns unfinished ones, and `None` means no filter on status.
- **Recurring tasks.**
    - `Task` got a `due_date` field, because "today + 1 day" needs a date to start from.
    - `Task.next_occurrence()` builds the next copy, using `timedelta(days=1)` for daily and `timedelta(weeks=1)` for weekly. It counts from the task's own `due_date`, so finishing a task late doesn't skip a day.
    - `Pet.complete_task()` marks the task done and attaches the next occurrence. `Scheduler.mark_task_complete()` finds the pet and calls it. The logic lives on `Pet` because a `Task` can't add itself to its pet's task list.
    - Task names are now only unique among a pet's incomplete tasks. Before, the new "Walk" would have been refused while the completed "Walk" still existed. Completed tasks stay as history.
- **Conflict detection.**
    - `Task` got an optional `start_time` ("HH:MM") and a `start_minutes` property that converts it to minutes after midnight.
    - `Scheduler.detect_conflicts()` returns a list of warning messages instead of raising an error. Two tasks conflict when their time ranges overlap on the same due date, for the same pet or different pets. Back-to-back tasks are not flagged, and tasks with no `start_time` are skipped.

**Phase 6: UI Polish**
- `generate_daily_plan()` takes an optional `plan_date`, so the plan only includes tasks due on or before that date. Without it, a recurring task's next occurrence (due tomorrow) showed up in today's plan.
- The UI needed a way to set the owner's available minutes per time block, because without it every block defaulted to 0 and every task was skipped.
- The UI also needed a way to remove a task, which uses `Pet.remove_task()`. I added it after I created a task that conflicted with another one and had no way to fix it.

**UML relationships added at the end.** The first UML only showed ownership (`Owner` has `Pet`s, `Pet` has `Task`s, `Scheduler` reads from `Owner`). I added the interactions that were missing:
- `Scheduler` plans `Task`s.
- `Scheduler.markTaskComplete` delegates to `Pet.completeTask`.
- `Pet.completeTask` creates the next `Task`, using `Task.nextOccurrence`, which creates a copy of the `Task`.
- `Owner.getAllTasks` collects tasks from all of its pets. Tasks live on pets, so this is a dashed (derived) link instead of ownership.

I also added parameters and return types to the methods, and a note that `Owner.constraints` keys and `Task.preferredTime` must come from `TIME_BLOCKS`.

**Working style note.** During this work I told Claude Code that I prefer regular multi-line `for` loops and multi-line conditionals over one-line versions. I describe that in section 2b.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

    - **Available time per time block.** The owner sets how many minutes they have in the morning, afternoon and evening (`Owner.constraints`). A task is only placed in a block if its duration fits in the minutes that block has left. A task longer than every block is skipped, and so is a task that fits nowhere. Each skipped task gets a reason.
    - **Priority.** Tasks are sorted by `Priority` (HIGH, MEDIUM, LOW) and then by shortest duration, so high-priority tasks claim time first.
    - **Preferred time of day.** Each task has a `preferred_time`. The scheduler tries that block first and falls back to the other blocks if it is full.
    - **Completion status and due date.** Completed tasks are never planned. When a plan date is given, only tasks due on or before that date are planned, so a recurring task's next occurrence does not show up early.
    - **Start times (warnings only).** An optional `start_time` is not used to place tasks. It is used to sort the task list and to warn about overlapping tasks with `detect_conflicts()`.

- How did you decide which constraints mattered most?

    - **Time came first because it is a hard limit.** The owner cannot do more than the minutes they have, so the scheduler never overfills a block.
    - **Priority came second.** When time is tight, the important tasks, like meals and medicine, should win over nice-to-haves. Sorting by priority before placing anything means a LOW task can never take space a HIGH task needed. Shortest duration breaks ties because it lets more tasks fit.
    - **Preferences came last because they are soft.** A task that cannot go in its preferred block is better moved to another block than dropped, so `preferred_time` is a preference and not a rule. The plan's explanation says when a task was moved and why, so the owner can see it.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

    - **Conflict detection only warns, and only checks tasks that have a `start_time`.**

    - `Scheduler.detect_conflicts()` 
        - returns a list of warning messages instead of raising an error or moving tasks around on its own. 
        - It flags two tasks as a conflict when their time ranges overlap (each one starts before the other ends) on the same due date, whether they belong to the same pet or different pets.
        - Back-to-back tasks (one ends at 08:30, the next starts at 08:30) are not flagged. 
        - It compares every pair of tasks (using `combinations()`), which gets slower as the task list grows. 
        - It also skips tasks that have no `start_time`, so tasks that `generate_daily_plan` only places into a time block are never checked against each other.

- Why is that tradeoff reasonable for this scenario?

    - This is reasonable for this scenario because an owner only has a handful of tasks per day, so comparing every pair is fast and easy to read. 

    - A warning lets the owner decide how to fix it, and the program never crashes. The downside is that the scheduler will not fix a conflict for the owner, and a conflict between two tasks without a `start_time` can go unnoticed.

**Code style preference saved for the AI assistant.**

While working on this step I told Claude Code that I prefer regular multi-line `for` loops over one-line loops, and multi-line conditionals over one-line conditionals, because the one-line versions are harder for me to read. Claude Code updated its memory files, `MEMORY.md` and `feedback_code-style-loops-conditionals.md`, to record this, so new code it writes for this project follows that style.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

    - **Creating the UML**: At first to practice and understand how to create UML diagrams, I prompted Claude Code to be a guide and to not give me the answer. I gave an attempt of my own to really understand the system the assignment asked to create. I used Claude Code to create the UML diagram with my ideas. Through collaboration, we created a UML diagram! After completing more steps in the assignment I realized I was missing things and use Claude code to update the UML diagram and add the missing fields and methods such as mark_complete in the `pawpal_system.py`.
    - **Creating the Classes and the CLI Demo on main.py**: I first gave an attempt at creating the classes. I then used Claude code to generate the rest of the logic. 

- What kinds of prompts or questions were most helpful? 
    - Since I was following along and doing my own attempts. I felt I was gathering more context. This allowed me to be more direct with my prompts. Also, what helped was using the instructions from the Codepath Class assignment as the prompt. This was direct and gave me what I needed.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    - In in the inital version of the UML diagram. We had a lot of back and forth conversations since I was still understanding the relationships with the entities used in the app.

- How did you evaluate or verify what the AI suggested?
    - I evaluated what the AI suggested by cross referencing my notes and understanding to see if made sense.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

    I wrote 25 automated tests with pytest in `tests/test_pawpal.py`. They cover:
    - **Basics (2 tests):** `mark_complete` changes a task's status, and adding a task to a pet increases its task count.
    - **Sorting (8 tests):**
        - Tasks come out in time-block order (morning, afternoon, evening).
        - Ties break by priority and then duration.
        - Within a block, tasks are ordered by `start_time`, with timed tasks before untimed ones.
        - A start time never overrides block order.
        - Sorting works across several pets.
        - Completed tasks are skipped.
        - No tasks gives an empty list.
    - **Recurring tasks (7 tests):**
        - Completing a daily task creates a task for the next day, and a weekly task creates one 7 days later.
        - Completing a one-time task creates nothing.
        - The next date counts from the task's `due_date`, not today.
        - Dates roll over the end of a month.
        - The original task is marked complete.
        - The new task keeps the original's details.
    - **Conflict detection (8 tests):**
        - It flags the same start time for one pet and across pets, and it flags partial overlaps.
        - It ignores back-to-back tasks, the same time on different days, completed tasks and tasks with no `start_time`.
        - No tasks gives an empty list.

- Why were these tests important?

    - **They protect the logic the plan depends on.** Sorting, recurrence and conflict detection are the parts that are easy to get subtly wrong, and a mistake would not crash the program. It would just give the owner a wrong schedule.
    - **Edge cases are where the bugs are.** Back-to-back tasks, month-end dates, and counting recurrence from `due_date` are all places where a "mostly right" version would pass a casual check. Testing them pinned the behavior down on purpose.
    - **They let me change things safely.** I changed `sort_by_time` after the first version (adding start times and an optional task list), and the tests showed the earlier ordering rules still held.

**b. Confidence**

- How confident are you that your scheduler works correctly?

    - **Very confident in sorting, recurring tasks and conflict detection.** All 25 tests pass, and they cover the normal cases and the tricky ones, like back-to-back tasks, month-end dates and counting recurrence from `due_date`.
    - **Less confident in the parts without automated tests.** `generate_daily_plan` (priority order, falling back to another block, skipping tasks that do not fit, and the plan-date filter), `filter_tasks`, `mark_task_complete`, `Pet.remove_task`, the `start_time` validation and the Streamlit UI. I checked those by running `main.py` and trying the app by hand, which is not as reliable as a test.

- What edge cases would you test next if you had more time?

    - **Planning:**
        - A HIGH task takes space before a LOW task, even when the LOW task was added first.
        - A task falls back to another block when its preferred block is full.
        - A task is skipped when it is longer than every block, and when it fits nowhere.
        - Only tasks due on or before `plan_date` are planned.
        - Running the plan twice gives the same result, and the owner's `constraints` are never changed.
    - **Filtering and completing:**
        - Combining `pet_name` and `completed` in `filter_tasks`.
        - `mark_task_complete` with an unknown pet or task raises `KeyError`.
        - Completing the same task twice.
    - **Time handling:**
        - `start_time` values like "8:30", "25:00" and "08:60" are rejected.
        - A task that runs past midnight, such as 23:50 for 30 minutes. Its end time would wrap around in the conflict message.
        - Three or more tasks that all overlap.
        - Weekly recurrence across a year end and a leap day.
    - **A known gap:** `generate_daily_plan` places tasks into time blocks but does not look at `start_time`, so a plan can put two tasks in a block whose start times conflict. Conflict detection warns about this, but the plan does not avoid it.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    - I am proud that I decided to go part by part. This helped me understand and not get lost when the LLM generated code. I felt that if I where to just give a big prompt or multiple questions then I would be more confused. I broke it down into parts which made it easier to follow along.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    - I would love to spend more time in the scheduler. I feel that is it the biggest part of the app and I would love to have more time to dig in and really plan out the features. I feel this would benefit from splitting up the work into multiple parts as I felt there was a lot of complexity into the scheduler that needed more time to really appreciate it.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    - This was my first time using LLM as a coding partner. I felt that I was following along and making the changes that we needed to complete the assignment. The important part I learned is to break down the problems part by part. If I were to give it a huge prompt, I felt the LLM would have made more errors than if you were doing it part by part. By breaking down the things to do, I felt the LLM to be more effective.

**d. Which AI coding assistant features were most effective for building your scheduler?**
- What really helped was the Claude Code knows which file you are working on. It also keeps a context and refers back to things that we had discussed.

**e. Give one example of an AI suggestion you rejected or modified to keep your system design clean.**
- For me to understand the code better, I did not like that Claude kept using one line for loops and one line conditionals. I prompted Claude to keep in mind to use regular for loops and multi-line conditionals. Claude updated `MEMORY.md` and now everytime it generate code it use a regular for loop and multi-line conditionals.

**f. How did using separate chat sessions for different phases help you stay organized?**
- I used to always use one chat, but I can now see the benefit of using multiple chat windows. This helps keep your work organized so that you start new chat for a new feature.

**g. Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.**
- This assignment truly made me feel like the Lead Architect! I was telling claude what to do and we worked together to create an app! This felt way faster than if I were to do it alone. 
    - I learned about:
        - Multiple chat windows to organize your work
        - Breaking down the problem into smaller tasks so that Claude can be more effective
