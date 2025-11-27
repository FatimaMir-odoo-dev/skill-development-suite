
from odoo import models, fields, api, _

class ConfirmDeleteSkill(models.TransientModel):
    _name = 'skill_development.delete_progress'
    _description = 'Confirm Skill Deletion Wizard'

    plan_id = fields.Many2one('skill_development.growth_tracker', string='Plan to Delete')

    def confirm_delete(self):
        self.ensure_one()
        self.plan_id.unlink()
        return {'type': 'ir.actions.act_window_close'}
