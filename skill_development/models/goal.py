# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api


class Goal(models.Model):
    _name = "skill_development.goal_project"
    _description = 'Skill'

    goal_name = fields.Char('Goal')
    # learner_id
    # related_task_id
    date_start = fields.Date(string='Start Date')
    date = fields.Date(string='Expiration Date', index=True, tracking=True)
    # result

class GoalTask(models.Model):
    _name = "skill_development.goal_task"
    _description = 'Skill'

    name = fields.Char('Task')
    # learner_id
    goal_id = fields.Many2one('skill_development.goal_project', string = 'Goal')
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






