# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError
# from odoo.tools import video as video_utils


class Goal(models.Model):
    _name = "skill_development.goal_project"
    _description = 'Skill'

    # Connects to the learner profile for security and filter?
    learner_id = fields.Many2one('res.users', string="Created by", required=True)
    # Connect to the learner's initial plan records to get all their skills
    learner_plan_record_ids = fields.Many2one('skill_development.initial_plan_record', string="Skill", required=True,
                                              # domain="[('plan_owner_id', '=', uid)]"
                                              )
    date_start = fields.Date(string='Start Date')
    date = fields.Date(string='Expiration Date', index=True, tracking=True)
    result_ids = fields.One2many('skill_development.goal_result', 'goal_id')
    task_ids = fields.One2many('skill_development.goal_task', 'goal_id', string='Tasks')
    goal_status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('finalized', 'Finalized'),
            ('complete', 'Complete')
        ], default='draft', string='Status', readonly=True)
    # is_complete = fields.Boolean(string="Goal Complete", default="False")
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
    goal_id = fields.Many2one('skill_development.goal_project', string='Goal')
    stage_id = fields.Many2one(
        'skill_development.goal_task_stage',
        string='Stage',
        domain="[('learner_id', '=', uid)]",
        ondelete='restrict',
        required='True'
    )
    # tag_id
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
    result = fields.Char(string="Expected Results")
    is_done = fields.Boolean('Achieved')

class LessonBank(models.Model):
    _name = 'skill_development.goal_lesson_bank'
    _description = 'Lesson Bank'

    learner_plan_record_ids = fields.Many2one('skill_development.initial_plan_record', string="Skill", required=True,)
    goal_id = fields.Many2one('skill_development.goal_project', 'Goal')
    lesson_title = fields.Char('Lesson')
    lesson = fields.Html(String='Scribbles', anitize_attributes=False)
