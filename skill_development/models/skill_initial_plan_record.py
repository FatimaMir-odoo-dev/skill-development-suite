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
    progress = fields.Float('Skill Progression')
    scribble_note = fields.Html('Scribbles')

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
