# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## Implementation Summary

pawpal_system.py contains the pet-care models and scheduling logic: a Pet stores Tasks, and an Owner manages multiple pets and preferences. Scheduler gathers tasks with their pets, orders eligible tasks by due time and priority, and returns a SchedulePlan with scheduled times and reasons for skipped tasks. Tasks can recur once, daily, or weekly; completing a recurring task through its Pet marks that occurrence complete and automatically adds a fresh next occurrence. Weekly tasks recur on the weekday they were created. Task queries and plans can be filtered by pet and completion status. Deadline conflicts are reported when earlier scheduled work leaves a task unable to finish by its due time, and `Scheduler.detect_conflicts` returns warnings for overlapping scheduled intervals without stopping the app. The demo in main.py prints a sample schedule and an overlap warning, and test_pawpal.py covers task management and scheduling behavior.

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

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule
Daily plan starting at 07:30 (60 minutes available). Tasks are ordered by due time, then priority:
- 07:30 — Breakfast for Mochi (10 min, high priority)
- 07:40 — Medication for Luna (5 min, high priority)
- 07:45 — Morning walk for Mochi (25 min, medium priority)
- Not scheduled: Nail trim for Mochi (Already completed.)
(.venv) linda@Lindas-MacBook-Pro ai110-module2show-pawpal-starter % git add .
(.venv) linda@Lindas-MacBook-Pro ai110-module2show-pawpal-starter % python3 main.py
Tasks sorted by due time:
- 08:00 — Breakfast
- 08:30 — Medication
- 09:00 — Morning walk
- 12:00 — Nail trim

Pending tasks for Mochi:
- Morning walk
- Breakfast

Completed tasks:
- Nail trim for Mochi

Conflict detection:
Warning: Morning walk for Mochi overlaps Medication for Luna from 08:00 to 08:05.

Today's Schedule
Daily plan starting at 07:30 (60 minutes available). Tasks are ordered by due time, then priority:
- 07:30 — Breakfast for Mochi (10 min, high priority)
- 07:40 — Medication for Luna (5 min, high priority)
- 07:45 — Morning walk for Mochi (25 min, medium priority)
- Not scheduled: Nail trim for Mochi (Already completed.)
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
| Task sorting | `Scheduler.sort_by_time`, `Scheduler.organize_tasks` | Sorts by earliest due time, placing tasks without due times last. Daily plans break matching due-time ties by priority (high, then medium, then low). |
| Filtering and eligibility | `Owner.get_all_tasks`, `Scheduler.filter_tasks`, `Scheduler.build_daily_plan` | Filter by pet and completion status. Plans exclude completed tasks, tasks matching owner `avoid:` preferences, and weekly tasks not due that day. |
| Time and deadlines | `Scheduler.organize_tasks` | Starts at the selected time, consumes each task's duration from the available-minute budget, and skips tasks that do not fit, run past midnight, or cannot finish by their due time. |
| Conflict warnings | `Scheduler.detect_conflicts` | Checks scheduled intervals pairwise and returns warning messages for overlaps, including across pets. This check is separate from daily plan generation. |
| Recurring tasks | `Task.frequency`, `Pet.complete_task` | Supports one-time, daily, and weekly tasks. Completing a recurring task adds its next occurrence; weekly tasks recur on their start weekday. |

## Testing PawPal+

Run the automated tests with:

```python -m pytest
```

The test suite checks task creation and completion, recurring task generation,
sorting and filtering, schedule deadlines and time limits, and overlap warnings.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
