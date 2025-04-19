# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api


class SkillPlanWizard(models.TransientModel):
    _name = 'skill_development.initial_plan_wizard'
    _description = 'Skill Planning Pop-up Form'

# learner_id used in default get form to get the current user id
    learner_id = fields.Many2one('res.users', string='Learner', required=True)

# form fields
    skill_name = fields.Char('Skill')
    motivation = fields.Text('My Motivation', required=True)
    endpoint = fields.Date('Preferred Endpoint')
    msg_2self = fields.Text('Message to Myself')

# get learner id and skill name from context passed to the wizard form
    @api.model
    def default_get(self, fields_list):
        res = super(SkillPlanWizard, self).default_get(fields_list)
        learner_id = self.env.context.get('default_learner_id')
        skill_name = self.env.context.get('default_skill_name')

        if learner_id:
            res['learner_id'] = learner_id  # Set the default value for learner_id
        if skill_name:
            res['skill_name'] = skill_name  # Set the default value for skill_name
        return res

    # create a new record in model skill_plan.record with all the data from the wizard
    def button_create_plan(self):
        self.env['skill_development.initial_plan_record'].create({
            'plan_owner_id': self.learner_id.id,
            'skill_name': self.skill_name,
            'motivation': self.motivation,
            'endpoint': self.endpoint,
            'msg_2self': self.msg_2self,
        })
        return {'type': 'ir.actions.act_window_close'}
