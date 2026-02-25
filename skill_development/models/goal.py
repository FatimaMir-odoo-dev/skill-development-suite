# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
"""
Skill Development - Personalized learning plans with SMART goals.

Enables learners to set goals, track progress, and reflect on their learning journey.

Main features:
    - SMART goal framework
    - Task and resource management
    - Progress tracking
    - Lesson bank for reflections
    - Customizable stages and tags
"""

import re
from random import randint

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from ..services.progress_logic_helper import ProgressLogicHelper


class Goal(models.Model):
    """SMART Goal model with progress tracking and status management."""

    _name = "skill_development.goal"
    _description = 'Goal'
    _inherit = 'count.mixin'
    _rec_name = 'goal_name'

    # 1. RELATIONAL FIELDS
    # ________________________________________
    # Used for the "Learner can only see own goals" record rule
    learner_id = fields.Many2one('res.users', string="Created by", required=True)

    # Needed to scope goals to a plan.
    learner_plan_id = fields.Many2one('skill_development.growth_tracker',
                                      string="Plan",
                                      ondelete='cascade')

    #  Needed to pass skill context to wizards and compute progress per skill.
    skill_id = fields.Many2one('skill_development.skill',
                               string="Main Skill",
                               readonly=True)

    result_ids = fields.One2many('skill_development.goal_result',
                                 'goal_id',
                                 string='Results')

    task_ids = fields.One2many('skill_development.task',
                               'goal_id',
                               string='Tasks')

    lesson_ids = fields.One2many('skill_development.lesson_bank',
                                 'goal_id',
                                 string=" ")

    tag_ids = fields.Many2many(
        'skill_development.tag',
        relation='goal_tag_rel',
        column1='goal_id',
        column2='tag_id',
        string='Tags',
    )
    # ________________________________________

    # 2. STATUS FIELDS
    # ________________________________________
    # for goal, task , result, resources lock
    is_acquired = fields.Boolean(
        string="Skill Acquired",
        related="learner_plan_id.is_acquired",
        store=True,
        readonly=True)

    goal_status = fields.Selection([
        ('draft', 'Draft'),
        ('finalized', 'Finalized'),
        ('complete', 'Complete')],
        default='draft',
        string='Status',
        readonly=True)

    date_start = fields.Date(string='Start Date')
    date = fields.Date(string='Expiration Date', index=True, tracking=True)
    # ________________________________________

    # 3. METRICS (COMPUTED)
    # ________________________________________
    goal_progress = fields.Float(
        string="Goal Contribution",
        compute='_compute_goal_progress',
        store=True)

    task_count = fields.Integer(string=" ", compute='_compute_task_count')

    lesson_count = fields.Integer(string=" ",
                                  compute='_compute_lesson_count')
    # ________________________________________

    # 4. SMART GOAL FIELDS
    # ________________________________________
    category = fields.Selection([
        ('knowledge', 'Knowledge'),
        ('practice', 'Practice'),
        ('creation', 'Creation & Contribution')],
        required=True)
    specific_goal = fields.Text('Specific goal category')
    measurable_goal = fields.Text("Measurable goal category'")
    achievable_goal = fields.Text('Achievable goal category')
    relevant_goal = fields.Text('Relevant goal category')
    timed_goal = fields.Text('Time-Bound goal category')
    goal_name = fields.Char('Complete Goal Statement')
    # ________________________________________

    # 5. FLAGS
    # ________________________________________
    # For locking goals, tasks, and resources
    is_complete = fields.Boolean(string="Goal Complete", default=False)

    # ====================================================================================================================
    # is_smart = fields.Boolean(string='SMART Compliant')
    # is_reflection_filled = fields.Boolean(string='Reflection Sheet Completed')

    @api.depends('goal_status', 'result_ids.is_done',
                 'specific_goal', 'measurable_goal', 'achievable_goal',
                 'relevant_goal', 'timed_goal',
                 'lesson_ids.lesson_worked', 'lesson_ids.lesson_change', 'lesson_ids.lesson_learned')
    def _compute_goal_progress(self):
        """
        Calculate the goal's percentage within its skill category.

        Progress is determined by each goal's:
        - Completion of SMART goal components
        - Achievement of expected results
        - Logged reflections and lessons learned
        """

        for goal in self:
            goal.goal_progress = ProgressLogicHelper.calculate_progress(goal)

    @api.depends('task_ids')
    def _compute_task_count(self):
        """Using the count_mixin to count tasks associated with each goal."""
        self._compute_count(
            count_field='task_count',
            counted_model='skill_development.task',
            related_field='goal_id'
        )

    @api.depends('lesson_ids')
    def _compute_lesson_count(self):
        """Using the count_mixin to count lessons associated with each goal."""
        self._compute_count(
            count_field='lesson_count',
            counted_model='skill_development.lesson_bank',
            related_field='goal_id'
        )

    @api.model_create_multi
    def create(self, vals_list):
        """Set default learner_id and learner_plan_id upon goal creation if missing."""
        for vals in vals_list:
            # Set learner_id to current user if not provided
            if 'learner_id' not in vals:
                vals['learner_id'] = self.env.user.id

            # Set learner_plan_id from context if not provided
            if not vals.get('learner_plan_id') and self.env.context.get('default_learner_plan_id'):
                vals['learner_plan_id'] = self.env.context.get('default_learner_plan_id')

        return super(Goal, self).create(vals_list)

    def action_create_goal_draft(self):
        """Set goal status to draft if planning on it is incomplete."""

        def action_create_goal_draft(self):
            for rec in self:
                if rec.goal_status != 'complete':
                    rec.goal_status = 'draft'

    def action_finalize_goal(self):
        """Finalize the goal plan when completed."""
        for rec in self:
            rec.goal_status = 'finalized'

    def action_complete_goal(self):
        """
        Set goal status to 'complete' and mark as complete.
        And returns an action to open the reflection wizard.
        """
        self.ensure_one()

        self.goal_status = 'complete'
        self.is_complete = True
        # rec._compute_goal_progress()

        return {
            'type': 'ir.actions.act_window',
            # this refers to the wizard form
            'res_model': 'skill_development.log_goal_lesson',
            'view_mode': 'form',
            'name': 'My Reflection',
            'target': 'new',
            'context': {  # Pass the learner ID to the wizard form
                'default_goal_id': self.id,
                'default_skill_id': self.skill_id.id,
                'default_learner_plan_id': self.learner_plan_id.id},  # Pass the skill name to the wizard form
        }

    def action_view_tasks(self):
        """
        Opens a view of all tasks related to this goal.
        Locks tasks if goal is completed or skill is marked as acquired.
        """
        self.ensure_one()

        if self.is_complete or self.is_acquired:
            action_ref = 'skill_development.task_lock_action'
        else:
            action_ref = 'skill_development.task_unlock_action'

        action = self.env.ref(action_ref).sudo().read()[0]

        # Inject domain and context dynamically
        action.update({
            'domain': [('goal_id', '=', self.id)],
            'context': {'default_goal_id': self.id}
        })

        return action

    # def action_view_tasks(self):
    #     _logger.info("Record ID %s: is_complete = %s", self.id, self.is_complete)
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Tasks',
    #         'res_model': 'skill_development.goal_task',
    #         'view_mode': 'kanban,form',
    #         'domain': [('goal_id', '=', self.id)],
    #         'context': {'default_goal_id': self.id,
    #                     },
    #     }

    def action_view_lesson(self):
        """ Opens a view of all lessons associated with this goal """

        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lesson',
            'res_model': 'skill_development.lesson_bank',
            'view_mode': 'tree,form',
            'domain': [('goal_id', '=', self.id)],
            'context': {'default_goal_id': self.id},
        }

    # def action_open_goal_popup(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'New Goal',
    #         'res_model': 'skill_development.goal_project',
    #         'view_mode': 'form',
    #         'target': 'new',
    #     }


class TaskStage(models.Model):
    """Task stages for organizing tasks in Kanban view within each goal."""

    _name = 'skill_development.task_stage'
    _description = 'Task Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True)

    learner_id = fields.Many2one('res.users', string='Owner', required=True,
                                 default=lambda self: self.env.user,
                                 index=True)
    goal_id = fields.Many2one('skill_development.goal', required=True, ondelete='cascade')

    sequence = fields.Integer(string='Sequence', default=10)
    fold = fields.Boolean(string='Folded in Kanban',
                          help='If enabled, this stage will be shown as folded in the Kanban view.')
    active = fields.Boolean(string='Active', default=True)

    # legend_blocked = fields.Char('Blocked Label', default='Blocked', required=True)
    # legend_done = fields.Char('Done Label', default='Ready', required=True)
    # legend_normal = fields.Char('Normal Label', default='In Progress', required=True)


class Task(models.Model):
    """Tasks for tracking progress within a goal.

    Each task represents a specific action item that contributes to completing
    a goal. Tasks can be organized by stages, prioritized, and linked to resources.
    """

    _name = "skill_development.task"
    _description = 'Task'
    _inherit = 'count.mixin'
    _rec_name = 'name'

    name = fields.Char('Task', required=True)
    description = fields.Html(string='Description')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High')],
        default='0', index=True, string="Priority", tracking=True)
    date_end = fields.Date(string='Ending Date', index=True, copy=False)

    learner_id = fields.Many2one('res.users', string='Owner', required=True,
                                 default=lambda self: self.env.user,
                                 index=True)
    # learner_skill_id = fields.Many2One('skill_development.growth_tracker', string="Skill", required=True,)
    goal_id = fields.Many2one('skill_development.goal', string='Goal', ondelete='cascade')
    stage_id = fields.Many2one('skill_development.task_stage',
                               string='Stage',
                               domain="[('learner_id', '=', learner_id)]",
                               ondelete='restrict',
                               required=True)
    tag_ids = fields.Many2many(
        'skill_development.tag',
        relation='task_tag_rel',
        column1='task_id',
        column2='tag_id',
        string="Tags"
    )
    is_goal_complete = fields.Boolean(string="Goal Completed", related="goal_id.is_complete")
    resource_ids = fields.One2many('skill_development.task_resource', 'task_id', string='Resources')

    resource_count = fields.Integer(string=' ', compute='_compute_resource_count')
    resource_url = fields.Char(string="Quick Access URL",
                               help="Enter a URL (web link) here for quick and easy access to external resources relevant to this task.")  # noqa: E501

    @api.depends('resource_ids')
    def _compute_resource_count(self):
        """Counts the number of resources linked to this task."""

        self._compute_count(
            count_field='resource_count',
            counted_model='skill_development.task_resource',
            related_field='task_id'
        )

    @api.model_create_multi
    def create(self, vals_list):
        """Prevent creating tasks for completed goals."""
        for vals in vals_list:
            goal_id = vals.get('goal_id') or self.env.context.get('default_goal_id')
            if goal_id:
                goal = self.env['skill_development.goal'].browse(goal_id)
                if goal.exists() and goal.is_complete:
                    raise ValidationError("Cannot add a task to a completed goal.")
        return super().create(vals_list)

    # @api.model
    # def create(self, vals):
    #     if not vals.get('stage_id') and vals.get('goal_id'):
    #         goal = self.env['skill_development.goal_project'].browse(vals['goal_id'])
    #         first_stage = self.env['skill_development.goal_task_stage'].search([
    #             ('goal_id', '=', goal.id)
    #         ], order='sequence', limit=1)
    #         vals['stage_id'] = first_stage.id if first_stage else False
    #     return super(Task, self).create(vals)


class TaskResource(models.Model):
    """Resources linked to tasks.

        Stores various types of learning resources (documents, links, pics, etc.)
        that support task completion.
        """

    _name = 'skill_development.task_resource'
    _description = 'Resource for Tasks'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Controls the display order of resources."
    )

    resource_type = fields.Selection([
        ('document', 'Document'),
        ('link', 'External Link'),
        ('tool', 'Tool/App'),
        ('video', 'Video'),
        ('image', 'Image'),
    ], string='Type', required=True)

    video = fields.Binary(string='Video', attachment=True)
    image = fields.Binary(string='Image', attachment=True)
    file = fields.Binary('Upload File', attachment=True)
    url = fields.Char('External URL')

    task_id = fields.Many2one('skill_development.task', string='Related Task', required=True, ondelete="cascade")
    # is_acquired = fields.Boolean(related="task_id.goal_id.learner_plan_id.is_acquired",
    #                              string="Skill Acquired" , store=False)

    # image_preview = fields.Binary(string='Image Preview')
    # video_preview = fields.(
    #     string='Video Preview',
    #     compute='_compute_video_preview',
    #     store=False,
    # )

    # @api.depends('video')
    # def _compute_video_preview(self):
    #     for rec in self:
    #         rec.video_preview = (
    #             video_utils.Video.from_binary(rec.video).preview_image()
    #             if rec.video else False
    #         )


class GoalResult(models.Model):
    """Expected results/outcomes for goals.

        Defines results that indicate goal completion.
        Each result can be marked as achieved to track progress.
        """

    _name = 'skill_development.goal_result'
    _description = 'Goal Results'
    _rec_name = 'result'

    goal_id = fields.Many2one('skill_development.goal', 'Goal', ondelete='cascade')
    result = fields.Text(string="Expected Results")
    is_done = fields.Boolean(string="Achieved")

    # Computed flag, not stored, not editable
    # is_not_done = fields.Boolean(
    #     string="Not Achieved",
    #     compute='_compute_is_not_done'
    # )
    #
    # @api.depends('is_done')
    # def _compute_is_not_done(self):
    #     for rec in self:
    #         rec.is_not_done = not rec.is_done


class LessonBank(models.Model):
    """Repository of lessons learned after goal completion.

    Captures reflections and insights gained after completing goals for future reference.
    """

    _name = 'skill_development.lesson_bank'
    _description = 'Lesson Bank'
    _rec_name = 'lesson_title'

    learner_id = fields.Many2one('res.users', string='Owner', required=True,
                                 default=lambda self: self.env.user,
                                 index=True)
    learner_plan_id = fields.Many2one(
        'skill_development.growth_tracker',
        string="Growth Plan",
        ondelete='cascade')
    goal_id = fields.Many2one('skill_development.goal', 'Goal', readonly=True)

    goal_skill = fields.Char(related='goal_id.skill_id.skill_name', string="Related Skill")
    lesson_title = fields.Char('Title', required=True)
    tag_ids = fields.Many2many('skill_development.tag',
                               relation='tag_lesson_rel',
                               column1='lesson_id',
                               column2='tag_id',
                               string="Tags"
                               )

    lesson_worked = fields.Html(string='What Worked')
    lesson_change = fields.Html(string='What to Change')
    lesson_learned = fields.Html(string='What Was Learned')
    extra_thoughts = fields.Html(string='Extra Thoughts')

    sequence = fields.Integer(string="Sequence", default=10)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High')],
        default='0', index=True, string="Priority")
    lesson_short = fields.Char(string="Lesson Preview", compute="_compute_lesson_short")

    @api.depends('lesson_worked')
    def _compute_lesson_short(self):
        """Generate a preview of the lesson by truncating the 'What Worked' field."""
        for record in self:
            plain = re.sub(r'<[^>]+>', '', record.lesson_worked or '')
            record.lesson_short = (plain[:50] + '...') if len(plain) > 50 else plain

    @api.onchange('goal_id')
    def _onchange_goal_id(self):
        """Auto-fills the plan when a goal is selected."""

        if self.goal_id and self.goal_id.learner_plan_id:
            self.learner_plan_id = self.goal_id.learner_plan_id
        else:
            self.learner_plan_id = False


class Tag(models.Model):
    """Tags for categorizing goals, tasks, and lessons.

    Provides a flexible labeling system to organize and filter
    learning activities across the skill development module.
    """

    _name = "skill_development.tag"
    _description = "Goal Tags"

    # Ensures no tag name is repeated for the user to avoid creating clutter
    _sql_constraints = [
        ('tag_name_unique', 'unique(name)', 'A tag with this name already exists.')
    ]

    name = fields.Char('Name', required=True)
    color = fields.Integer(
        string='Color',
        default=lambda self: randint(1, 11),
        help="Color used in Kanban or labels.")
