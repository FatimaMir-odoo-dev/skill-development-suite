# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from random import randint
from ..services.skill_growth_logic_helper import GoalLogicHelper



class Goal(models.Model):
    _name = "skill_development.goal_project"
    _description = 'Skill'

    # Connects to the learner profile for security and filter?
    learner_id = fields.Many2one('res.users', string="Created by", required=True)
    # Connect to the learner's initial plan records to get all their skills
    learner_plan_record_ids = fields.Many2one('skill_development.initial_plan_record', string="Skill", required=True,
                                              # domain="[('plan_owner_id', '=', uid)]"
                                              )
    skill_id = fields.Many2one('skill_development.skill_record', string="Main Skill", readonly=True)
    date_start = fields.Date(string='Start Date')
    date = fields.Date(string='Expiration Date', index=True, tracking=True)
    result_ids = fields.One2many('skill_development.goal_result', 'goal_id', string=' ')
    task_ids = fields.One2many('skill_development.goal_task', 'goal_id', string='Tasks')
    tag_ids = fields.Many2many('skill_development.goal_tag', string="Tags")

    goal_status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('finalized', 'Finalized'),
            ('complete', 'Complete')
        ], default='draft', string='Status', readonly=True)

    is_complete = fields.Boolean(string="Goal Complete", default="False")
    goal_progress = fields.Float(string="Goal Contribution", compute='_compute_goal_progress')
    lesson_id = fields.One2many('skill_development.goal_lesson_bank','goal_id')

    @api.depends('goal_status', 'result_ids.is_done',
                 'specific_goal', 'measurable_goal', 'achievable_goal',
                 'relevant_goal', 'timed_goal',
                 'lesson_id.lesson_worked', 'lesson_id.lesson_change', 'lesson_id.lesson_learned')
    def _compute_goal_progress(self):
        for goal in self:
            goal.goal_progress = GoalLogicHelper.calculate_progress(goal)

    category = fields.Selection([
        ('knowledge', 'Knowledge'),
        ('practice', 'Practice'),
        ('creation', 'Creation & Contribution')
    ], required=True)

    # is_smart = fields.Boolean(string='SMART Compliant')
    # is_reflection_filled = fields.Boolean(string='Reflection Sheet Completed')

    # Contents of SMART Goal record
    specific_goal = fields.Text('Specific: [What exactly do you want to achieve?]')
    measurable_goal = fields.Text("Measurable: [How do you know if you're progress is good?]")
    achievable_goal = fields.Text('Achievable: [what makes you sure you can do it?]')
    relevant_goal = fields.Text('Relevant: [Why is it important to you? (think of your motivation)]')
    timed_goal = fields.Text('Time-Bound: [What is your timeline?]')
    goal_name = fields.Text('Complete Goal Statement')
    task_count = fields.Integer(string=' ', compute='_compute_task_count')
    kanban_state = fields.Selection([
        ('normal', 'On Hold'),
        ('done', 'In Progress'),
        ('blocked', 'Canceled')],
        string='Status', default='normal')


    @api.constrains('name')
    def _check_SMART_fields(self):
        for record in self:
            if record.name:
                # Check if all the other fields are filled before allowing `name` field
                if not (
                        record.specific_goal and record.measurable_goal and record.achievable_goal and record.relevant_goal and record.timed_goal):
                    raise ValidationError(
                        "To make your goal really effective, please make sure all SMART fields are filled out accurately."
                        " before entering the final goal statement.\n"
                        "Take your time and think about each guideline carefully for the best results.")

    @api.model
    def create(self, vals):
        if 'learner_id' not in vals:
            vals['learner_id'] = self.env.user.id
        return super(Goal, self).create(vals)

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

        learner = self.env['res.users'].search([('id', '=', self.env.uid)], limit=1)
        learner_id = learner.id if learner else False

        return {
            'type': 'ir.actions.act_window',
            # this refers to the wizard form
            'res_model': 'skill_development.goal_lesson_bank_wizard',
            'view_mode': 'form',
            'name': 'My Reflection',
            'target': 'new',
            'context': {
                'default_learner_plan_record_ids': self.learner_plan_record_ids.id,  # Pass the learner ID to the wizard form
                'default_goal_id': self.id,
                },  # Pass the skill name to the wizard form
        }

    def action_view_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'skill_development.goal_task',
            'view_mode': 'kanban,form',
            'domain': [('goal_id', '=', self.id)],
            'context': {'default_goal_id': self.id},
        }

    def action_view_lesson(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lesson',
            'res_model': 'skill_development.goal_lesson_bank',
            'view_mode': 'tree,form',
            'domain': [('goal_id', '=', self.id)],
            'context': {'default_goal_id': self.id},
        }

    def _compute_task_count(self):
        for record in self:
            record.task_count = self.env['skill_development.goal_task'].search_count(
                [('goal_id', '=', record.id)])

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


class GoalStage(models.Model):
    _name = 'skill_development.goal_task_stage'
    _description = 'Task Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True)
    learner_id = fields.Many2one('res.users', string='Owner', required=True, default=lambda self: self.env.user,
                              index=True)
    sequence = fields.Integer(string='Sequence', default=1)
    fold = fields.Boolean(string='Folded in Kanban',
                           help='If enabled, this stage will be shown as folded in the Kanban view.')
    active = fields.Boolean(string='Active', default=True)

    legend_blocked = fields.Char('Blocked Label', default='Blocked', required=True)
    legend_done = fields.Char('Done Label', default='Ready', required=True)
    legend_normal = fields.Char('Normal Label', default='In Progress', required=True)

    # task_id
    # goal_id


class GoalTask(models.Model):
    _name = "skill_development.goal_task"
    _description = 'Skill'

    name = fields.Char('Task')
    # learner_id
    # learner_plan_record_ids = fields.Many2one('skill_development.initial_plan_record', string="Skill", required=True,)
    goal_id = fields.Many2one('skill_development.goal_project', string='Goal')
    stage_id = fields.Many2one(
        'skill_development.goal_task_stage',
        string='Stage',
        domain="[('learner_id', '=', uid)]",
        ondelete='restrict',
        required='True'
    )
    tag_ids = fields.Many2many('skill_development.goal_tag', string="Tags")
    description = fields.Html(string='Description', anitize_attributes=False)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High')],
        default='0', index=True, string="Priority", tracking=True)
    # create_date = fields.Datetime("Created On", readonly=True)
    # write_date = fields.Datetime("Last Updated On", readonly=True)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    resource_url = fields.Char('Quick Access URL')
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')],
        string='Status',default='normal')
    resource_ids = fields.One2many('skill_development.goal_task_resource', 'task_id', string='Resources')

    # def action_open_resource_form(self):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Add Resource',
    #         'res_model': 'skill_development.goal_task_resource',
    #         'view_mode': 'form',
    #         'target': 'new',  # or 'current' for full-page
    #         'context': {
    #             'default_name': 'Default Resource Name',
    #             'default_resource_type': 'document',
    #             # you can pass more defaults here
    #         }
    #     }


class GoalResource(models.Model):
    _name = 'skill_development.goal_task_resource'
    _description = 'Resource for Tasks'

    name = fields.Char('Name', required=True)
    resource_type = fields.Selection([
        ('document', 'Document'),
        ('link', 'External Link'),
        ('tool', 'Tool/App'),
        ('video', 'Video'),
        ('image', 'Image'),
    ], string='Type', required=True)

    file = fields.Binary('Upload File')
    url = fields.Char('External URL')
    task_id = fields.Many2one('skill_development.goal_task', string='Related Task')  # Replace with your task model
    description = fields.Text('Description')
    video = fields.Binary(string='Video', attachment=True)
    image = fields.Binary(string='Image', attachment=True)
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

    goal_id = fields.Many2one('skill_development.goal_project', 'Goal')
    result = fields.Text(string="Expected Results")
    is_done = fields.Boolean("Achieved")
    is_not_done = fields.Boolean("Not Achieved", compute='_compute_is_not_done', inverse='_inverse_is_not_done')

    @api.depends('is_done')
    def _compute_is_not_done(self):
        for rec in self:
            rec.is_not_done = not rec.is_done

    def _inverse_is_not_done(self):
        for rec in self:
            rec.is_done = not rec.is_not_done


class LessonBank(models.Model):
    _name = 'skill_development.goal_lesson_bank'
    _description = 'Lesson Bank'

    learner_plan_record_ids = fields.Many2one('skill_development.initial_plan_record', string="Skill", required=True,)
    goal_id = fields.Many2one('skill_development.goal_project', 'Goal', readonly=True)
    lesson_title = fields.Char('Title')

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
    tag_ids = fields.Many2many(
        'skill_development.goal_tag',
        relation='goal_tag_rel',
        column1='goal_id',
        column2='tag_id',
        string="Tags"
    )

    @api.model
    def create(self, vals):
        if vals.get('goal_id'):
            goal = self.env['skill_development.goal_project'].browse(vals['goal_id'])
            if goal.learner_plan_record_ids:
                vals['learner_plan_record_ids'] = goal.learner_plan_record_ids.id
        return super().create(vals)

    def write(self, vals):
        if vals.get('goal_id'):
            goal = self.env['skill_development.goal_project'].browse(vals['goal_id'])
            if goal.learner_plan_record_ids:
                vals['learner_plan_record_ids'] = goal.learner_plan_record_ids.id
        return super().write(vals)

    @api.depends('lesson_worked')
    def _compute_lesson_short(self):
        for record in self:
            record.lesson_short = (record.lesson_worked[:50] + '...') if record.lesson_worked and len(
                record.lesson_worked) > 50 else record.lesson_worked

    @api.onchange('goal_id')
    def _onchange_goal_id(self):
        if self.goal_id and self.goal_id.learner_plan_record_ids:
            self.learner_plan_record_ids = self.goal_id.learner_plan_record_ids
        else:
            self.learner_plan_record_ids = False

    def name_get(self):
        lesson = []
        for record in self:
            # Return the skill_name as the display name in the learner_skill_id dropdown
            name = record.lesson_title or "Unnamed Lesson"
            lesson.append((record.id, name))
        return lesson


class GoalTags(models.Model):
    _name = "skill_development.goal_tag"
    _description = "Goal Tags"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Name', required=True, unique=True)  # Unique name field
    color = fields.Integer(string='Color', default=_get_default_color, help="Color for the tag")

    goal_ids = fields.Many2many('skill_development.goal_project', 'goal_project_tags_rel', string='Projects')
    task_ids = fields.Many2many('skill_development.goal_task', string='Tasks')
    lesson_id = fields.Many2many(
        'skill_development.goal_lesson_bank',
        relation='tag_lesson_rel',
        column1='tag_id',
        column2='lesson_id',
        string='Lesson'
    )