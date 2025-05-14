# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api, exceptions
from random import randint


class SkillRecord(models.Model):
    _name = "skill_development.skill_record"
    _description = 'Skill'


    # Skill Record Details:
    skill_name = fields.Char(string='Skill Name', required=True)
    description = fields.Text(string='Skill Description', required=True)
    # learn = fields.Char(string="")
    # difficulty = fields.
    # rating_ids
    career_path_ids = fields.Many2many('skill_development.career_path',
                                       relation='skill_career_rel',
                                       column1='skill_id',
                                       column2='career_id',
                                       string='Job roles for this skill')

    related_skill_ids = fields.Many2many('skill_development.skill_record',  relation='skill_related_rel',
                                       column1='skill_id',
                                       column2='related_id',
                                       string='Related Skills',
                                       domain="[('id', '!=', id)]")

    pre_requisites = fields.Text(string="Pre-Requisites")
    prereq_skill_ids = fields.Many2many('skill_development.skill_record',  relation='skill_prereq_rel',
                                           column1='skill_id',
                                           column2='rprereq_id',
                                           string='Consider Learning First',
                                           domain="[('id', '!=', id)]")

    is_transferable = fields.Boolean(string="This Skill is Transferable")

    @api.model
    def unlink(self):
        for record in self:
            record.career_path_ids = [(5, 0, 0)]  # Clear the many2many links
        return super(SkillRecord, self).unlink()



    # Check if the Skill Name is unique to prevent duplicated skill creation
    @api.constrains('skill_name')
    def _check_unique_skill_name(self):
        for record in self:
            existing_skill = self.search([('skill_name', '=', record.skill_name), ('id', '!=', record.id)])
            if existing_skill:
                raise exceptions.ValidationError(
                    "A skill with the same name already exists. Please refer back to it or use a different name.")

    # Opens the wizard form for the skill's initial plan.
    # Activated upon clicking the Button: Start Learning
    @api.model
    def action_open_initial_plan_wizard(self, context=None):

        # get the Learner ID to pass it tp the wizard form in context
        learner = self.env['res.users'].search([('id', '=', self.env.uid)], limit=1)
        learner_id = learner.id if learner else False

        return {
            'type': 'ir.actions.act_window',
            # this refers to the wizard form
            'res_model': 'skill_development.initial_plan_wizard',
            'view_mode': 'form',
            'name': 'My Skill Plan',
            'target': 'new',
            'context': {
                'default_learner_id': learner_id,},  # Pass the learner ID to the wizard form
            'default_skill_name': self.skill_name,  # Pass the skill name to the wizard form
        }

# Get the Skill Name to be used by other records
    def name_get(self):
        result = []
        for record in self:
            name = record.skill_name  # Only use skill_name, without the ID or extra Info
            result.append((record.id, name))
        return result

class CareerPath(models.Model):
    _name = "skill_development.career_path"
    _description = "Skill Career Paths"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Career", required=True)
    description = fields.Text(string="")
    industry_ids = fields.Many2many('skill_development.industry',
                                    relation='career_industry_rel',
                                    column1='career_id',
                                    column2='industry_id',
                                    string="Industries")
    color = fields.Integer(string='Color', default=_get_default_color, help="Color for the career tag")

    @api.model
    def unlink(self):
        for record in self:
            record.industry_ids = [(5, 0, 0)]  # Clear the many2many links
        return super(CareerPath, self).unlink()

class Industry(models.Model):
    _name = "skill_development.industry"
    _description = "Skill Career Paths Industries"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Industry Name', required=True, unique=True)  # Unique name field
    color = fields.Integer(string='Color', default=_get_default_color, help="Color for the Industry tag")

    # career_ids = fields.Many2many('skill_development.skill_career', string="")