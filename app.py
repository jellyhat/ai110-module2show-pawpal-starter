from collections import defaultdict, deque
from datetime import time as datetime_time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owners" not in st.session_state:
    existing_owner = st.session_state.get("owner")
    st.session_state["owners"] = (
        [existing_owner] if isinstance(existing_owner, Owner) else []
    )

owners = st.session_state["owners"]

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+, a pet care planner for managing pets, care tasks, and daily schedules.
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
- Add pets and track their care tasks.
- Build a daily schedule that considers due times, priorities, and available time.
- Explain which tasks were scheduled and why others were skipped.
"""
    )

st.divider()

st.subheader("Add an Owner")
with st.form("add_owner_form", clear_on_submit=True):
    owner_name = st.text_input("Owner name")
    add_owner = st.form_submit_button("Add owner")

if add_owner:
    try:
        owners.append(Owner(name=owner_name.strip()))
    except ValueError as error:
        st.error(str(error))
    else:
        st.success(f"Added owner {owner_name.strip()}.")

owner = None
if owners:
    owner_labels = [
        f"{index + 1}. {registered_owner.name}"
        for index, registered_owner in enumerate(owners)
    ]
    selected_owner_label = st.selectbox(
        "Select owner to manage",
        options=owner_labels,
        key="active_owner",
    )
    owner = owners[owner_labels.index(selected_owner_label)]
else:
    st.info("Add an owner before adding pets or care tasks.")

st.divider()

st.subheader("Add a Pet")
if owners:
    pet_owner_options = ["Select an owner"] + owner_labels
    with st.form("add_pet_form", clear_on_submit=True):
        pet_name = st.text_input("Pet name")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        selected_pet_owner_label = st.selectbox(
            "Owner (required)", options=pet_owner_options
        )
        add_pet = st.form_submit_button("Add pet")

    if add_pet:
        if selected_pet_owner_label == "Select an owner":
            st.error("Select an owner for this pet.")
        else:
            selected_pet_owner = owners[
                owner_labels.index(selected_pet_owner_label)
            ]
            try:
                selected_pet_owner.add_pet(
                    Pet(name=pet_name.strip(), species=species)
                )
            except ValueError as error:
                st.error(str(error))
            else:
                st.success(
                    f"Added {pet_name.strip()} to "
                    f"{selected_pet_owner.name}'s pets."
                )

if owner is not None and owner.pets:
    st.caption(
        f"Pets for {owner.name}: "
        + ", ".join(f"{pet.name} ({pet.species})" for pet in owner.pets)
    )
else:
    st.info("Add a pet to the selected owner before creating a care task.")

st.divider()

st.subheader("Add a Care Task")
if owner is not None and owner.pets:
    pet_options = [
        f"{index + 1}. {pet.name} ({pet.species})"
        for index, pet in enumerate(owner.pets)
    ]
    with st.form("add_task_form", clear_on_submit=True):
        selected_pet_label = st.selectbox("Pet", options=pet_options)
        task_title = st.text_input("Task title")
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox(
            "Repeats", ["once", "daily", "weekly"]
        )
        has_due_time = st.checkbox("Set a due time")
        due_time_input = st.time_input(
            "Due time", value=datetime_time(17, 0)
        )
        add_task = st.form_submit_button("Add task")

    if add_task:
        selected_pet = owner.pets[pet_options.index(selected_pet_label)]
        due_time = due_time_input if has_due_time else None
        try:
            selected_pet.add_task(
                Task(
                    title=task_title.strip(),
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=frequency,
                    due_time=due_time,
                )
            )
        except ValueError as error:
            st.error(str(error))
        else:
            st.success(f"Added {task_title.strip()} for {selected_pet.name}.")

tasks = owner.get_all_tasks() if owner is not None else []
if tasks:
    scheduler = Scheduler()
    st.markdown("### Current Tasks")
    pet_filter = st.selectbox(
        "Filter by pet",
        ["All pets"] + [pet.name for pet in owner.pets],
        key="task_pet_filter",
    )
    status_filter = st.selectbox(
        "Filter by status",
        ["all", "pending", "completed"],
        key="task_status_filter",
    )
    visible_tasks = scheduler.filter_tasks(
        tasks,
        pet_name=None if pet_filter == "All pets" else pet_filter,
        status=status_filter,
    )
    completed_task_ids = {
        id(pet_task.task)
        for pet_task in scheduler.filter_tasks(tasks, status="completed")
    }
    pending_task_ids = {
        id(pet_task.task)
        for pet_task in scheduler.filter_tasks(tasks, status="pending")
    }
    pet_tasks_by_task_id = defaultdict(deque)
    for pet_task in visible_tasks:
        pet_tasks_by_task_id[id(pet_task.task)].append(pet_task)
    sorted_visible_tasks = [
        pet_tasks_by_task_id[id(task)].popleft()
        for task in scheduler.sort_by_time(
            [pet_task.task for pet_task in visible_tasks]
        )
    ]
    st.table(
        [
            {
                "Pet": pet_task.pet.name,
                "Task": pet_task.task.title,
                "Duration (minutes)": pet_task.task.duration_minutes,
                "Priority": pet_task.task.priority,
                "Due by": (
                    pet_task.task.due_time.strftime("%H:%M")
                    if pet_task.task.due_time
                    else "No deadline"
                ),
                "Repeats": pet_task.task.frequency,
                "Status": (
                    "Completed"
                    if id(pet_task.task) in completed_task_ids
                    else "Pending"
                ),
            }
            for pet_task in sorted_visible_tasks
        ]
    )
    for index, pet_task in enumerate(sorted_visible_tasks):
        if id(pet_task.task) in pending_task_ids and st.button(
            f"Mark {pet_task.task.title} for {pet_task.pet.name} complete",
            key=f"complete_task_{index}",
        ):
            pet_task.pet.complete_task(pet_task.task)
            st.rerun()

st.divider()

if owner is not None:
    st.subheader("Build Schedule")
    with st.form("schedule_form"):
        available_minutes = st.number_input(
            "Time available today (minutes)",
            min_value=0,
            max_value=1440,
            value=240,
        )
        day_start = st.time_input("Start time", value=datetime_time(8, 0))
        schedule_pet = st.selectbox(
            "Schedule pet",
            ["All pets"] + [pet.name for pet in owner.pets],
            key="schedule_pet_filter",
        )
        schedule_status = st.selectbox(
            "Schedule task status",
            ["all", "pending", "completed"],
            index=1,
        )
        generate_schedule = st.form_submit_button("Generate schedule")

    if generate_schedule:
        if not tasks:
            st.info("Add at least one task before generating a schedule.")
        else:
            plan = scheduler.build_daily_plan(
                owner,
                available_minutes=int(available_minutes),
                day_start=day_start,
                pet_name=None if schedule_pet == "All pets" else schedule_pet,
                status=schedule_status,
            )
            st.markdown("### Daily Plan")
            st.info(scheduler.explain_plan(plan))
            conflict_warnings = scheduler.detect_conflicts(plan.scheduled)
            if conflict_warnings:
                for warning in conflict_warnings:
                    st.warning(warning)
            else:
                st.success("No overlapping tasks in this schedule.")

            if plan.scheduled:
                st.dataframe(
                    [
                        {
                            "Start": entry.start_time.strftime("%H:%M"),
                            "Pet": entry.pet.name,
                            "Task": entry.task.title,
                            "Duration (minutes)": entry.task.duration_minutes,
                            "Priority": entry.task.priority,
                        }
                        for entry in plan.scheduled
                    ],
                    hide_index=True,
                    width="stretch",
                )
            if plan.skipped:
                st.markdown("#### Skipped tasks")
                st.table(
                    [
                        {
                            "Pet": entry.pet.name,
                            "Task": entry.task.title,
                            "Reason": entry.reason,
                        }
                        for entry in plan.skipped
                    ]
                )
