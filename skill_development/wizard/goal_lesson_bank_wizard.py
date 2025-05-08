# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api


class SkillPlanWizard(models.TransientModel):
    _name = 'skill_development.goal_lesson_bank_wizard'
    _description = 'Lesson Bank Pop-up Form'

    learner_plan_record_ids = fields.Many2one('skill_development.initial_plan_record', string="Skill", required=True, readonly=True)
    goal_id = fields.Many2one('skill_development.goal_project', 'Goal', readonly=True)
    lesson_title = fields.Char('Lesson')
    lesson_worked = fields.Html(String='What Worked', sanitize_attributes=False)
    lesson_change = fields.Html(String='What to Change', sanitize_attributes=False)
    lesson_learned = fields.Html(String='What Was Learned', sanitize_attributes=False)
    extra_thoughts = fields.Html(String='Extra Thoughts', sanitize_attributes=False)

    def button_save_lesson(self):
        self.env['skill_development.goal_lesson_bank'].create({
            'lesson_title': self.lesson_title,
            'lesson_worked': self.lesson_worked,
            'lesson_change': self.lesson_change,
            'lesson_learned': self.lesson_learned,
            'extra_thoughts': self.extra_thoughts,
        })
        return {'type': 'ir.actions.act_window_close'}


