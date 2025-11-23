# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api


class SkillPlanWizard(models.TransientModel):
    _name = 'skill_development.lesson_bank_wizard'
    _description = 'Lesson Bank Pop-up Form'

    goal_id = fields.Many2one('skill_development.goal', 'Goal', readonly=True, required=True,)
    skill_id = fields.Many2one('skill_development.skill_record', string="Skill", readonly=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'High')],
        default='0', index=True, string="Priority")
    tag_ids = fields.Many2many(
        'skill_development.tag',
        relation='wizard_tag_lesson_rel',
        column1='tag_id',
        column2='lesson_id',
        string='Tags'
    )
    lesson_title = fields.Char('Lesson')
    lesson_worked = fields.Html(String='What Worked', sanitize_attributes=False)
    lesson_change = fields.Html(String='What to Change', sanitize_attributes=False)
    lesson_learned = fields.Html(String='What Was Learned', sanitize_attributes=False)
    extra_thoughts = fields.Html(String='Extra Thoughts', sanitize_attributes=False)

    def button_save_lesson(self):
        self.env['skill_development.lesson_bank'].create({
            'lesson_title': self.lesson_title,
            'lesson_worked': self.lesson_worked,
            'lesson_change': self.lesson_change,
            'lesson_learned': self.lesson_learned,
            'extra_thoughts': self.extra_thoughts,
            'skill_id': self.skill_id.id,
            'priority': self.priority,
            'goal_id': self.goal_id.id,
            'tag_ids': [(6, 0, self.tag_ids.ids)],
        })
        return {'type': 'ir.actions.act_window_close'}


