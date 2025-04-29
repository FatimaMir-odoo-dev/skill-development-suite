# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api


class SkillPlanWizard(models.TransientModel):
    _name = 'skill_development.goal_lesson_bank_wizard'
    _description = 'Lesson Bank Pop-up Form'

    learner_plan_record_ids = fields.Many2one('skill_development.initial_plan_record', string="Skill", required=True, readonly=True)
    goal_id = fields.Many2one('skill_development.goal_project', 'Goal', readonly=True)
    lesson_title = fields.Char('Lesson')
    lesson = fields.Html(String='Scribbles', anitize_attributes=False)

    def button_save_lesson(self):
        self.env['skill_development.goal_lesson_bank'].create({
            'lesson_title': self.lesson_title,
            'lesson': self.lesson,
        })
        return {'type': 'ir.actions.act_window_close'}


