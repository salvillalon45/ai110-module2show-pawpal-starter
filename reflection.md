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


### After starting Phase 3: UI and Backend Integration
For the Pet class I added a new field called species since I noticed the UI had it.

### After starting Phase 4: Algorithmic Layer
- For the `Scheduler` class I added:
    - `sort_by_time`
    - `filter_tasks`
    - `markTaskComplete()` 
    - `detectConflicts()`
- For the `Task` class I added:
    - `markComplete()`
    - `nextOccurrence()`
    - `startMinutes()`
- For the `Pet` class I added:
    - `completeTask()`
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

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
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
