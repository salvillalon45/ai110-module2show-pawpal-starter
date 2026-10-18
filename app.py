import streamlit as st
from pawpal_system import Owner, Pet, Task, Priority, Frequency

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name)

# Always update the owner_name in the case the user renames it
st.session_state.owner.name = owner_name

if st.button("Add a Pet"):
    try:
        st.session_state.owner.add_pet(Pet(pet_name, species))
        st.success(f"Added {pet_name}")
    except ValueError as e:
        st.error(str(e))

# The owner's pets list is the single source of truth for which pets exist
pet_names = []
for pet in st.session_state.owner.pets:
    pet_names.append(pet.name)

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    title = st.text_input("Task title", value="Morning walk")
with col2:
    description = st.text_input("Task Description", value="walk in the local park nearby")
with col3:  
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col4:
    priority = st.selectbox("Priority", [Priority.LOW, Priority.MEDIUM, Priority.HIGH], index=2)
with col5:
    preferred_time = st.selectbox("Preferred Time", ["morning", "afternoon", "evening"], index=1)
with col6:
    frequency = st.selectbox("Frequency", [Frequency.ONCE, Frequency.DAILY, Frequency.WEEKLY], index=1)

if not pet_names:
    st.info("Add a pet before adding tasks.")
else:
    selected_pet_name = st.selectbox("Assign task to pet", pet_names)

    if st.button("Add task"):
        try:
            task = Task(
                title,
                description,
                duration,
                priority,
                preferred_time,
                frequency,
            )
            # Find the selected pet on the owner and add the task to it
            for pet in st.session_state.owner.pets:
                if pet.name == selected_pet_name:
                    pet.create_task(task)
                    break
            st.success(f"Added {title} to {selected_pet_name}")
        except ValueError as e:
            st.error(str(e))

all_tasks = st.session_state.owner.get_all_tasks()
if len(all_tasks) > 0:
    st.write("Current tasks:")
    # Build readable rows so the table shows names and labels instead of raw values
    rows = []
    for task in all_tasks:
        rows.append({
            "Pet": task.pet_name,
            "Task": task.name,
            "Description": task.description,
            "Minutes": task.duration,
            "Priority": task.priority.name,
            "Time": task.preferred_time,
            "Frequency": task.frequency.value,
            "Done": "✅" if task.completion_status else "⬜",
        })
    st.table(rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )
