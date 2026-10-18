# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🛠️ Implementation Summary

The logic layer lives in `pawpal_system.py`; `main.py` is a CLI demo that builds sample data and prints a plan.

**How the classes fit together**

- `Task` is a single care item: name, duration (minutes), `Priority`, a `preferred_time` block, a `Frequency`, and a completion flag. It validates its own input and has `mark_complete()`.
- `Pet` owns a list of tasks. Tasks are added through `Pet.create_task`, which stamps the task with the pet's name and keeps task names unique per pet. It also includes the functionality to edit and remove tasks from a Pet.
- `Owner` owns the pets and the time constraints: the minutes available in each block (`morning`, `afternoon`, `evening`). `Owner.get_all_tasks()` flattens every pet's tasks into one list.
- `Scheduler` takes an `Owner` and produces the plan. It reads from the owner but never changes the owner's data.

**How a plan is built**

1. `generate_daily_plan()` collects the owner's incomplete tasks and sorts them by priority, then by duration.
2. It works from a copy of the owner's constraints. For each task it tries the preferred block first, then the remaining blocks in order, and subtracts the task's duration from the first block with enough time left.
3. A task is skipped, with a recorded reason, if it is longer than every block or if no block has enough time left.
4. Each placement or skip is recorded under a `(pet name, task name)` key in `placement_reasons` or `skipped_tasks`.
5. `generate_explanation_of_plan()` turns those records into the readable text stored in `explanation_of_plan`.

Running `generate_daily_plan()` again rebuilds the plan from scratch, so it is safe to call after editing tasks.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```python
(.venv) ➜  codepath/codepath-ai/ai110-module2show-pawpal-starter git:(main) ✗ python3 main.py
Morning (55/60 min used):
  - Rex: prep meal (20 min) - placed in preferred block 'morning' (HIGH priority)
  - Buddy: prep meal (20 min) - placed in preferred block 'morning' (HIGH priority)
  - Buddy: nail trim (15 min) - placed in preferred block 'morning' (MEDIUM priority)
Afternoon (0/0 min used):
  (nothing scheduled)
Evening (60/90 min used):
  - Rex: walk (30 min) - preferred 'morning' was full; moved to 'evening' (HIGH priority)
  - Buddy: walk (30 min) - preferred 'morning' was full; moved to 'evening' (HIGH priority)

Skipped:
  - Rex: bath - 120 min is longer than any available time block (longest is 90 min)
  - Buddy: full groom - 150 min is longer than any available time block (longest is 90 min)
  - Rex: play fetch - no block has 40 min left (remaining: {'morning': 5, 'afternoon': 0, 'evening': 30})
(.venv) ➜  codepath/codepath-ai/ai110-module2show-pawpal-starter git:(main) ✗ 
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `sort_by_time` | Return incomplete tasks ordered by _preferred time block_ (morning afternoon, evening), then _highest priority_ first, then _shortest duration_ first. Tasks in the same block with the same priority are ordered by duration. Doesn't modify the plan or any task. |
| Filtering | `filter_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None)` | Return the owner's tasks matching the given filters. `pet_name`: only tasks belonging to that pet (None = all pets). `completed`: True = only finished tasks, False = only unfinished tasks (None = both). Filters combine, so both can be given at once. |
| Conflict handling | `detect_conflicts` | Return a warning message for every pair of overlapping timed tasks. Only incomplete tasks with a `start_time` are checked, and only tasks due on the same date can conflict. Two tasks overlap when each starts before the other ends (back-to-back tasks don't count). Pairs can belong to the same pet or different pets. Never raises; an empty list means no conflicts. |
| Recurring tasks | `next_occurrence` | Return an incomplete copy due on the next occurrence, or `None` for `ONCE` tasks. Daily tasks move forward 1 day and weekly tasks 7 days, counted from this task's `due_date` (not today), so finishing a task late doesn't skip a day. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
