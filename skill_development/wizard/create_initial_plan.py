# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import api, fields, models  # noqa: F401


class CreateInitialPlan(models.TransientModel):
    """
    Initial Skill Plan Wizard.
    Collects learner input and creates a corresponding growth tracker record.
    """

    _name = 'skill_development.create_initial_plan'
    _description = 'Skill Planning Pop-up Form'

# learner_id used in default get form to get the current user id
    learner_id = fields.Many2one(
        'res.users',
        string='Learner',
        required=True,
        default=lambda self: self.env.user,
        help="The learner this plan will be created for."
    )

# form fields
    skill_id = fields.Many2one('skill_development.skill', 'Skill', readonly=True)
    motivation = fields.Text('My Motivation', required=True)
    endpoint = fields.Date('Preferred Endpoint')
    msg_2self = fields.Text('Message to Myself')

# get learner id and skill name from context passed to the wizard form
#     @api.model
#     def default_get(self, fields_list):
#         res = super(SkillPlanWizard, self).default_get(fields_list)
#         learner_id = self.env.context.get('default_learner_id')
#         skill_id = self.env.context.get('default_skill_id')
#
#         if learner_id:
#             res['learner_id'] = learner_id  # Set the default value for learner_id
#         if skill_id:
#             res['skill_id'] = skill_id  # Set the default value for skill_name
#         return res

    def button_create_plan(self):
        """
        Transfers the entered values to a skill growth tracker record
        and closes the wizard window.
        """

        self.env['skill_development.growth_tracker'].create({
            'plan_owner_id': self.learner_id.id,
            'skill_id': self.skill_id.id,
            'motivation': self.motivation,
            'endpoint': self.endpoint,
            'msg_2self': self.msg_2self,
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Plan Created!',
                'message': 'Your growth plan has been added to your Skill Growth tracker.',
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
