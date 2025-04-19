# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SmartGoal(models.Model):
    _inherit = 'project.project'
    _description = 'To Manage the goals related to the Skills'

# Connects to the learner profile for security and filter?
    learner_id = fields.Many2one('res.users', string="Created by", required=True)
# Connect to the learner's initial plan records to get all their skills
    learner_plan_record_ids = fields.Many2one('skill_development.initial_plan_record', string ="Skill", required =True,
                                        domain="[('plan_owner_id', '=', uid)]")
# # To extract only the Skill Names off the learner's records
#     skill_name = fields.Char(string='Skill Name', related='learner_plan_record_ids.skill_name', store=True, readonly=True)

# Connecting the goal with its expected results
    expected_result_ids = fields.One2many('skill_development.smart_goal_result', 'smart_goal_id', string =" ")

# Contents of SMART Goal record
    specific_goal = fields.Text('Specific: [What exactly do you want to achieve?]')
    measurable_goal = fields.Text("Measurable: [How do you know if you're progress is good?]")
    achievable_goal = fields.Text('Achievable: [what makes you sure you can do it?]')
    relevant_goal = fields.Text('Relevant: [Why is it important to you? (think of your motivation)]')
    timed_goal = fields.Text('Time-Bound: [What is your timeline?]')
    name = fields.Text('Complete Goal Statement')

    @api.constrains('name')
    def _check_SMART_fields(self):
        for record in self:
            if record.name:
                # Check if all the other fields are filled before allowing `name` field
                if not (
                        record.specific_goal and record.measurable_goal and record.achievable_goal and record.relevant_goal and record.timed_goal):
                    raise ValidationError(
                        "To make your goal really effective, please make sure all SMART fields are filled out accurately."
                        " before entering the final goal statement.\n"
                        "Take your time and think about each guideline carefully for the best results.")

    @api.model
    def create(self, vals):
        if 'learner_id' not in vals:
            vals['learner_id'] = self.env.user.id
        return super(SmartGoal, self).create(vals)



class SmartGoalResult(models.Model):
    _name = 'skill_development.smart_goal_result'
    _description = 'Description'
    _auto = True

    smart_goal_id = fields.Many2one('project.project', 'Pointer')
    result = fields.Char(string="Expected Results")
    is_done = fields.Boolean('Achieved')