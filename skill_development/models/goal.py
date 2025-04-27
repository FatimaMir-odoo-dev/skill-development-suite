# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from xlsxwriter.contenttypes import defaults


class Goal(models.Model):
    _name = "skill_development.goal_project"
    _description = 'Skill'

    # Connects to the learner profile for security and filter?
    learner_id = fields.Many2one('res.users', string="Created by", required=True)
    # Connect to the learner's initial plan records to get all their skills
    learner_plan_record_ids = fields.Many2one('skill_development.initial_plan_record', string="Skill", required=True,
                                              # domain="[('plan_owner_id', '=', uid)]"
                                              )
    goal_name = fields.Char('Goal')
    # learner_id
    # related_task_id
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

    # Contents of SMART Goal record
    specific_goal = fields.Text('Specific: [What exactly do you want to achieve?]')
    measurable_goal = fields.Text("Measurable: [How do you know if you're progress is good?]")
    achievable_goal = fields.Text('Achievable: [what makes you sure you can do it?]')
    relevant_goal = fields.Text('Relevant: [Why is it important to you? (think of your motivation)]')
    timed_goal = fields.Text('Time-Bound: [What is your timeline?]')
    name = fields.Text('Complete Goal Statement')

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

    def action_finalize_goal(self):
        for rec in self:
            rec.goal_status = 'finalized'

    def action_complete_goal(self):
        for rec in self:
            rec.goal_status = 'complete'

    def action_view_tasks(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tasks',
            'res_model': 'skill_development.goal_task',
            'view_mode': 'kanban,form',
            'domain': [('goal_id', '=', self.id)],
            'context': {'default_goal_id': self.id},
        }


class GoalTask(models.Model):
    _name = "skill_development.goal_task"
    _description = 'Skill'

    name = fields.Char('Task')
    # learner_id
    goal_id = fields.Many2one('skill_development.goal_project', string='Goal')
    # stage_id
    # tag_id
    description = fields.Html(string='Description', anitize_attributes=False)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High'),
    ], default='0', index=True, string="Priority", tracking=True)
    # create_date = fields.Datetime("Created On", readonly=True)
    # write_date = fields.Datetime("Last Updated On", readonly=True)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    resources_url = fields.Char('URL for Resources')


class GoalResult(models.Model):
    _name = 'skill_development.goal_result'
    _description = 'Goal Results'
    _auto = True

    goal_id = fields.Many2one('skill_development.goal_project', 'Goal')
    result = fields.Char(string="Expected Results")
    is_done = fields.Boolean('Achieved')
