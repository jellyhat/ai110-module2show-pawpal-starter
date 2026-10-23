# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
1. A user should be able to add their pet(s) to this app.
2. They should be able to input what the pet specifically needs (meds, health concerns, appointments)
3. They should be able to add and edit tasks to their pet's schedule (maybe walks or trips)

Pet Class - pet details and tasks that a pet needs

Task Class -  an activity that relates to a pet, with a time and frequency and completion status

Owner Class -  can own multiple pets and their tasks. should be able to see all their tasks

Scheduler - The "Brain" that retrieves, organizes, and manages tasks across pets. It must read from that Owner method rather than from a single pet, or it will not earn the multi-pet point.
- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The UML design has one brain class that cascades down from Owner, to Pet, to each individual Task. Each (multiple) Task belongs to a Pet, an Owner can have multiple pets and the Scheduler can start planning based on that.



**b. Design changes**

- Did your design change during implementation?

Yes, after reviewing with my agent, it brought up that the Task relationship was not so concrete and could be refined.
- If yes, describe at least one change and why you made it.

We ended up making sure each Task had a pet it belongs to, adjusted the scheduler so that it would be able to know all this and have each pet association with each task.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
It considers avaliable time, priority, the task times and owner preferences. I think these are the basic constraints that should matter and should cover most cases, any others seemed too esoteric.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff is simple ordering in organize_tasks(). It orders by due time, priority and schedules in that order and doesn't try to optimize more to fit in more tasks/priorities. I think it would be a bit hard to compute that and seems like an edge case if you have that many tasks for one dog and that many needs.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
