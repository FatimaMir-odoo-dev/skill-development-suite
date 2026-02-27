
from odoo import api, fields, models  # noqa: F401


class DeleteProgress(models.TransientModel):
    """
    Confirmation wizard for deleting a skill growth plan.
    """

    _name = 'skill_development.delete_progress'
    _description = 'Confirm Skill Deletion Wizard'

    plan_id = fields.Many2one('skill_development.growth_tracker',
                              string='Plan to Delete',
                              required=True,
                              ondelete='cascade')

    def confirm_delete(self):
        self.ensure_one()
        self.plan_id.unlink()
        return {'type': 'ir.actions.act_window_close'}
