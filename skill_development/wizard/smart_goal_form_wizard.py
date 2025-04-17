from odoo import fields, models, api
from odoo.exceptions import ValidationError


class SmartGoalForm(models.TransientModel):
    _inherit = 'project.project'
    _description = 'To Manage the goals and tasks related to the Skills'

# Connects to the learner profile for security and filter?
#     learner_id = fields.Many2one('res.users', string="Created by", required=True)
# Connect to the skill_plan_record to get the Learners skill names
    learner_plan_record_ids = fields.Many2one('skill_development.initial_plan_record', string ="Learner Skills", required =True,
                                        domain="[('plan_owner_id', '=', uid)]")
    # skill_name = fields.Char(string='Skill Name', related='learner_plan_record_ids.skill_name', store=True, readonly=True)

# Contents of SMART Goal pop-up
    specific_goal = fields.Text('Specific: [What exactly do you want to achieve?]')
    measurable_goal = fields.Text("Measurable: [How do you know if you're progress is good?]")
    achievable_goal = fields.Text('Achievable: [what makes you sure you can do it?]')
    relevant_goal = fields.Text('Relevant: [Why is it important to you? (think of your motivation)]')
    timed_goal = fields.Text('Time-Bound: [What is your timeline?]')
    name = fields.Text('Complete Goal Statement')

    # @api.model
    # def create(self, vals):
    #     if 'learner_id' not in vals:
    #         vals['learner_id'] = self.env.user.id
    #     return super(SmartGoalForm, self).create(vals)

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
