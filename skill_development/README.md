# Skill Development
## Description
The **Skill Development** module is the core of the Skill Development Suite. It allows individuals to **create personal skill growth plans** using SMART goals, structured tasks, and relevant resources to enhance their learning and track their growth.

## Key Features
- Skill catalog managed by General Managers
- Personal learning plans with motivation, tracking, and deadlines
- Structured SMART goal template
- Goal decomposition into tasks with priorities, stages, and deadlines
- Progress tracking across three weighted categories:
  - Knowledge (15%)
  - Practice (35%)
  - Creation & Contribution (50%)
- Mastery titles: Seeker → Learner → Skilled → Proficient → Master
- Lesson bank for capturing reflections after goal completion
- Skill ratings submitted by learners after acquiring a skill
- Private progress — each learner's data is only visible to them

## Example Workflow
1. **General Manager** defines skills relevant to the organization (e.g. "Public Speaking", "Data Analysis").
2. **Learner** selects a skill, states their motivation and personal deadline, and creates a growth plan.
3. Learner builds a **SMART goal** — e.g. "Deliver a 10-minute speech at a community event by June 30."
4. Goal is broken into **tasks** with priorities, stages, and deadlines.
5. Learner attaches **resources** (videos, articles, links) to relevant tasks.
6. On goal completion, learner marks the goal as "complete" and logs **lessons learned**.
7. **Skill progress and mastery title** update automatically based on completed goals.
8. When satisfied, learner **marks the skill as acquired** and submits a rating.

## Dependencies
This module depends on the following Odoo core modules:
* `base`
* `hr`
> **Optional UI Enhancement:**
> For a more responsive user interface, install the [`web_responsive`](https://github.com/OCA/web/tree/16.0/web_responsive) 
> module from OCA. It is not required for core functionality and can be safely omitted 
> if your Odoo UI is already customized.

## Installation
See the [suite-level README](../README.md) for installation instructions.

## Access Control 
|User Role          |Permissions                                                                          |
|:------------------|:--------------------------------------------------------------------|
|General Manager    |Manage the skill catalog     				          |
|Learner 	    |Create and manage personal plans, goals, and tasks, and add resources|

## Screenshots
*Coming soon — Skill Catalog, Skill Growth Overview, SMART Goal Template, Task Breakdown.*
