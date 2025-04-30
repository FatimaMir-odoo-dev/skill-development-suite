# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SkillPlan(models.Model):
    _name = 'skill_development.initial_plan_record'
    _description = 'A Record For The Learner Skill Plan'

    # Record content
    plan_owner_id = fields.Many2one('res.users', string='Owner of the Plan', readonly=True)

    skill_name = fields.Char(string="Skill", readonly=True)
    motivation = fields.Text(string="Motivation to Learn")
    endpoint = fields.Date(string="Learning Endpoint")
    msg_2self = fields.Text(string="Message to Myself")
    progress_knowledge = fields.Float('Knowledge Progression')
    progress_practice = fields.Float('Practice Progression')
    progress_contribute = fields.Float('Creation & Contribution Progression')
    scribble_note = fields.Html(String='Scribbles', anitize_attributes=False)
    overall_progress = fields.Float(string="Overall Progress (%)", compute="_compute_overall_progress", store=True)

    title = fields.Selection([
        ('seeker', 'Seeker'),
        ('learner', 'Learner'),
        ('skilled', 'Skilled'),
        ('proficient', 'Proficient'),
        ('master', 'Master')
    ], default='seeker', string='Title', compute='_compute_title', store=True)

    @api.depends('progress_knowledge', 'progress_practice', 'progress_contribute')
    def _compute_overall_progress(self):
        for rec in self:
            rec.overall_progress = (rec.progress_knowledge * 0.15) + (rec.progress_practice * 0.35) + (
                        rec.progress_contribute * 0.5)

    @api.depends('overall_progress')
    def _compute_title(self):
        for rec in self:
            if rec.overall_progress >= 100:
                rec.title = 'master'
            elif rec.overall_progress >= 75:
                rec.title = 'proficient'
            elif rec.overall_progress >= 50:
                rec.title = 'skilled'
            elif rec.overall_progress >= 5:
                rec.title = 'learner'
            else:
                rec.title = 'seeker'

    def goals_button(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'My Goals',
            'res_model': 'skill_development.goal_project',
            'view_mode': 'kanban,form',
            'target': 'self',
        }

    # @api.model
    # def open_wizard_form(self, context=None):
    #
    #     # get the Learner ID to pass it tp the wizard form in context
    #     employee = self.env['res.users'].search([('id', '=', self.env.uid)], limit=1)
    #     learner_id = employee.id if employee else False
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         # this refers to the wizard form
    #         'res_model': 'skill_plan.form',
    #         'view_mode': 'form',
    #         'name': 'My Skill Plan',
    #         'target': 'new',
    #         'context': {
    #             'default_learner_id': learner_id},  # Pass the learner ID to the wizard form
    #         'default_skill_name': self.skill_name,  # Pass the skill name to the wizard form
    #     }

    # Python constraint to get a unique skill name (the user must create only one plan per skill)
    @api.constrains('skill_name')
    def _check_unique_skill_name(self):
        for record in self:
            # Ensure that the skill name is unique for the current user (record_learner_id)
            if self.search_count([
                ('skill_name', '=', record.skill_name),
                ('plan_owner_id', '=', record.plan_owner_id.id)
            ]) > 1:
                raise ValidationError(
                    f"The skill '{record.skill_name}' already exists for this user.\n"
                    f"You can update it by going to your profile and editing the plan record."
                )
    def name_get(self):
        result = []
        for record in self:
            # Return the skill_name as the display name in the learner_skill_id dropdown
            name = record.skill_name or "Unnamed Skill"
            result.append((record.id, name))
        return result

    # Ensures plan_owner_id is automatically set to the current user
    @api.model
    def create(self, vals):
        vals.setdefault('plan_owner_id', self.env.user.id)
        return super(SkillPlan, self).create(vals)

    # For the Smart Goal wizard where a learner can select one of the
    # skills saved in this record to connect the goal to



class LearnerProfile(models.Model):
    _inherit = "res.users"

# # Connect the learner to his volunteering record
#     volunteer_record_id = fields.Many2one('volunteer_request.record', string="Volunteering Record ID")
# Connect the learner to his skill plans record (used to save the data in Learner Profile)
    plan_skill_ids = fields.One2many('skill_development.initial_plan_record', 'plan_owner_id', string='Skill Plans')

# Here the data from skill_plan_record are displayed in the Learner Profile
    #record_skill_name = fields.Char(related="plan_skill_ids.skill_name", string="Skill")
    #record_skill_motive = fields.Text(related="plan_skill_ids.motivation" ,string="Motivation to Learn")
    #record_learning_endpoint = fields.Date(related="plan_skill_ids.endpoint" ,string="Learning Endpoint")
    #record_msg_2self = fields.Text(related="plan_skill_ids.msg_2self" ,string="Message to Myself")
