# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import api, fields, models  # noqa: F401


class ProgressGuide(models.TransientModel):
    """
    Skill Progress Help Wizard.

    Interactive help dialog that explains how skill progress,
    categories, and titles are calculated for a skill growth plan.
    """

    _name = 'skill_development.progress_guide'
    _description = 'Help / Skill Growth Guide'

    step = fields.Selection([
        ('page1', 'Overview'),
        ('page2', 'Details')
    ], default='page1', store=True)

    skill_plan_id = fields.Many2one('skill_development.growth_tracker')

    title = fields.Selection([
        ('seeker', 'Seeker'),
        ('learner', 'Learner'),
        ('skilled', 'Skilled'),
        ('proficient', 'Proficient'),
        ('master', 'Master')
    ], default='seeker', string='Title', readonly=True)

    overall_progress = fields.Float()
    maximum_progress = fields.Integer(string="Maximum Rate", default=100)

    def _navigate_to(self, step):
        """To navigate between the two pages of the help wizard."""
        self.ensure_one()
        self.write({'step': step})
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def go_to_page1(self):
        """Return the wizard to the first help page."""
        return self._navigate_to('page1')

    def go_to_page2(self):
        """Switch the wizard to the next page of the help guide."""
        return self._navigate_to('page2')
