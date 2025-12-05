# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from random import randint
from ..services.progress_logic_helper import ProgressLogicHelper
import logging
_logger = logging.getLogger(__name__)



class Goal(models.Model):
    _name = "skill_development.goal"
    _description = 'Goal'
    _inherit = 'count.mixin'

    # 1. RELATIONAL FIELDS
# ________________________________________
# Connects to the learner profile for security and filter? (why do we need it?)
    learner_id = fields.Many2one('res.users',string="Created by",required=True)

# Connect to the learner's growth records to get all their skills (why do we need to connect it?)
    learner_plan_id = fields.Many2one('skill_development.growth_tracker',
        string="Plan",
        ondelete='cascade')

# why do we need to connect with the original skill??
    skill_id = fields.Many2one('skill_development.skill',
        string="Main Skill",
        readonly=True)

    result_ids = fields.One2many('skill_development.goal_result',
        'goal_id',
        string='Results')

    task_ids = fields.One2many('skill_development.task',
        'goal_id',
        string='Tasks')

    lesson_id = fields.One2many('skill_development.lesson_bank',
        'goal_id',
        string=" ")

    tag_ids = fields.Many2many('skill_development.tag',string="Tags")
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

    kanban_state = fields.Selection([
        ('normal', 'On Hold'),
        ('done', 'In Progress'),
        ('blocked', 'Canceled')],
        string='Status',
        default='normal')

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

    lesson_count = fields.Integer(string=" ",compute='_compute_lesson_count')
# ________________________________________

    # 4. SMART GOAL FIELDS
# ________________________________________
    category = fields.Selection([
        ('knowledge', 'Knowledge'),
        ('practice', 'Practice'),
        ('creation', 'Creation & Contribution')],
        required=True)
    specific_goal = fields.Text('Specific: [What exactly do you want to achieve?]')
    measurable_goal = fields.Text("Measurable: [How do you know if your progress is good?]")
    achievable_goal = fields.Text('Achievable: [What makes you sure you can do it?]')
    relevant_goal = fields.Text('Relevant: [Why is it important to you?]')
    timed_goal = fields.Text('Time-Bound: [What is your timeline?]')
    goal_name = fields.Text('Complete Goal Statement')
# ________________________________________

    # 5. FLAGS
# ________________________________________
    #For locking goals, tasks, and resources
    is_complete = fields.Boolean(string="Goal Complete", default=False)

#====================================================================================================================
    # is_smart = fields.Boolean(string='SMART Compliant')
    # is_reflection_filled = fields.Boolean(string='Reflection Sheet Completed')

    # @api.constrains('goal_name')
    # def _check_SMART_fields(self):
    #     for record in self:
    #         if record.name:
    #             # Check if all the other fields are filled before allowing `name` field
    #             if not (
    #                     record.specific_goal and record.measurable_goal and record.achievable_goal and record.relevant_goal and record.timed_goal):
    #                 raise ValidationError(
    #                     "To make your goal really effective, please make sure all SMART fields are filled out accurately."
    #                     " before entering the final goal statement.\n"
    #                     "Take your time and think about each guideline carefully for the best results.")

    @api.depends('goal_status', 'result_ids.is_done',
                 'specific_goal', 'measurable_goal', 'achievable_goal',
                 'relevant_goal', 'timed_goal',
                 'lesson_id.lesson_worked', 'lesson_id.lesson_change', 'lesson_id.lesson_learned')

    def _compute_goal_progress(self):
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

    @api.depends('lesson_id')
    def _compute_lesson_count(self):
        """Using the count_mixin to count lessons associated with each goal."""
        self._compute_count(
            count_field='lesson_count',
            counted_model='skill_development.lesson_bank',
            related_field='goal_id'
        )

    @api.model_create_multi
    def create(self, vals_list):
        """Set default learner_id and learner_plan_id if not provided."""
        for vals in vals_list:
            # Set learner_id to current user if not provided
            if 'learner_id' not in vals:
                vals['learner_id'] = self.env.user.id

            # Set learner_plan_id from context if not provided
            if not vals.get('learner_plan_id') and self.env.context.get('default_learner_plan_id'):
                vals['learner_plan_id'] = self.env.context.get('default_learner_plan_id')

        return super(Goal, self).create(vals_list)

    def action_create_goal_draft(self):
        for rec in self:
            rec.goal_status = 'draft'

    def action_finalize_goal(self):
        for rec in self:
            rec.goal_status = 'finalized'

    def action_complete_goal(self):
        for rec in self:
            rec.goal_status = 'complete'
            rec.is_complete = True
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
                'default_learner_plan_id':self.learner_plan_id.id},  # Pass the skill name to the wizard form
        }

    def action_view_tasks(self):
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
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lesson',
            'res_model': 'skill_development.lesson_bank',
            'view_mode': 'tree,form',
            'domain': [('goal_id', '=', self.id)],
            'context': {'default_goal_id': self.id},
        }

    def name_get(self):
        result = []
        for record in self:
            # Return the skill_name as the display name in the learner_skill_id dropdown
            name = record.goal_name or "Unnamed Goal"
            result.append((record.id, name))
        return result

    # def action_open_goal_popup(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'New Goal',
    #         'res_model': 'skill_development.goal_project',
    #         'view_mode': 'form',
    #         'target': 'new',
    #     }


class TaskStage(models.Model):
    _name = 'skill_development.task_stage'
    _description = 'Task Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True)

    learner_id = fields.Many2one('res.users', string='Owner', required=True,
                default=lambda self: self.env.user,
                index=True)
    goal_id = fields.Many2one('skill_development.goal')

    sequence = fields.Integer(string='Sequence', default=1)
    fold = fields.Boolean(string='Folded in Kanban',
                           help='If enabled, this stage will be shown as folded in the Kanban view.')
    active = fields.Boolean(string='Active', default=True)

    # legend_blocked = fields.Char('Blocked Label', default='Blocked', required=True)
    # legend_done = fields.Char('Done Label', default='Ready', required=True)
    # legend_normal = fields.Char('Normal Label', default='In Progress', required=True)

class Task(models.Model):
    _name = "skill_development.task"
    _description = 'Task'
    _inherit = 'count.mixin'

    name = fields.Char('Task')
    description = fields.Html(string='Description', sanitize_attributes=False)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High')],
        default='0', index=True, string="Priority", tracking=True)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)

    # learner_id
    # learner_skill_id = fields.Many2One('skill_development.growth_tracker', string="Skill", required=True,)
    goal_id = fields.Many2one('skill_development.goal', string='Goal', ondelete='cascade')
    stage_id = fields.Many2one('skill_development.task_stage',
        string='Stage',
        domain="[('learner_id', '=', user_id)]",
        ondelete='restrict',
        required=True)
    tag_ids = fields.Many2many('skill_development.tag', string="Tags")
    is_goal_complete = fields.Boolean(string="Skill Acquired", related="goal_id.is_complete")
    resource_ids = fields.One2many('skill_development.task_resource', 'task_id', string='Resources')

    resource_count = fields.Integer(string=' ', compute='_compute_resource_count')
    resource_url = fields.Char(string="Quick Access URL",
            help="Enter a URL (web link) here for quick and easy access to external resources relevant to this task.")

    @api.depends('resource_ids')
    def _compute_resource_count(self):
        """Using the count_mixin to count resources associated with each task."""

        self._compute_count(
            count_field='resource_count',
            counted_model='skill_development.task_resource',
            related_field='task_id'
        )

    @api.model
    def create(self, vals):
        goal_id = vals.get('goal_id') or self.env.context.get('default_goal_id')

        if goal_id:
            goal = self.env['skill_development.goal'].browse(goal_id)

            if goal.exists() and goal.is_complete:
                raise ValidationError("Cannot add a task to a completed goal.")

        return super().create(vals)

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
    _name = 'skill_development.task_resource'
    _description = 'Resource for Tasks'

    name = fields.Char('Name', required=True)
    description = fields.Text('Description')

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

    task_id = fields.Many2one('skill_development.task', string='Related Task', ondelete="cascade")
    # is_acquired = fields.Boolean(related="task_id.goal_id.learner_plan_id.is_acquired", string="Skill Acquired" , store=False)

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
    _name = 'skill_development.goal_result'
    _description = 'Goal Results'
    _auto = True

    goal_id = fields.Many2one('skill_development.goal', 'Goal')
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
    _name = 'skill_development.lesson_bank'
    _description = 'Lesson Bank'

    learner_plan_id = fields.Many2one(
        'skill_development.growth_tracker',
        string="Plan",
        ondelete='cascade')

    skill_id = fields.Many2one('skill_development.skill', string="Skill")
    goal_id = fields.Many2one('skill_development.goal', 'Goal', readonly=True)

    goal_skill = fields.Char(related='goal_id.skill_id.skill_name', string="Skill")
    lesson_title = fields.Char('Title')
    tag_ids = fields.Many2many('skill_development.tag',
        relation='goal_tag_rel',
        column1='goal_id',
        column2='tag_id',
        string="Tags"
    )

    lesson_worked = fields.Html(string='What Worked', sanitize_attributes=False)
    lesson_change = fields.Html(string='What to Change', sanitize_attributes=False)
    lesson_learned = fields.Html(string='What Was Learned', sanitize_attributes=False)
    extra_thoughts = fields.Html(string='Extra Thoughts', sanitize_attributes=False)

    sequence = fields.Integer(string="Sequence", default=10)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High')],
        default='0', index=True, string="Priority")
    lesson_short = fields.Html(string="Lesson Preview", compute="_compute_lesson_short", sanitize_attributes=False)


    @api.depends('lesson_worked')
    def _compute_lesson_short(self):
        for record in self:
            record.lesson_short = (record.lesson_worked[:50] + '...') if record.lesson_worked and len(
                record.lesson_worked) > 50 else record.lesson_worked

    @api.onchange('goal_id')
    def _onchange_goal_id(self):
        if self.goal_id and self.goal_id.learner_plan_id:
            self.learner_plan_id = self.goal_id.learner_plan_id
        else:
            self.learner_plan_id = False

    def name_get(self):
        lesson = []
        for record in self:
            # Return the skill_name as the display name
            name = record.lesson_title or "Unnamed Lesson"
            lesson.append((record.id, name))
        return lesson


class Tag(models.Model):
    _name = "skill_development.tag"
    _description = "Goal Tags"

    _sql_constraints = [
        ('tag_name_unique', 'unique(name)', 'A tag with this name already exists.')
    ]

    name = fields.Char('Name', required=True)  # Unique name field
    color = fields.Integer(
        string='Color',
        default=lambda self: randint(1, 11),
        help="Color used in Kanban or labels.")

    goal_ids = fields.Many2many('skill_development.goal', 'goal_project_tags_rel', string='Projects')
    task_ids = fields.Many2many('skill_development.task', string='Tasks')
    tag_ids = fields.Many2many(
        'skill_development.lesson_bank',
        relation='tag_lesson_rel',
        column1='tag_id',
        column2='lesson_id',
        string='Lesson'
    )
