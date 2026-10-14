# Brainstorm the main objects needed for the system. For each object, determine:
- What information it needs to hold (attributes)
- What actions it can perform (methods)

Classes: Owner, Pet, Scheduler, Task

Owner Class
Attributes:
- name
- pet
- list of tasks
- constraints: Available time per day
Methods:
- createTask()
- editTask()

Pet Class
Attributes:
- name
Methods:

Scheduler Class
Attributes:
- owner
- plan: A dictionary that holds
- explanation of plan
- list of skipped tasks and skipped task explanation: A dictionary with the title of the task as the key and the explanation of the task as the value.
Methods:
- generateDailyPlan()
- generateExplainationOfPlan()

Task
Attributes:
- duration
- priority : string "high", "medium", "low" that will be mapped to 1,2,3 respectfully.
- name
- description
- preferred time: "morning", "afternoon", "evening"
- completionStatus: boolean
Method: