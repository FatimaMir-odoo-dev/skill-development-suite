# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from email.policy import default

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class SkillPlan(models.Model):
    _name = 'skill_development.initial_plan_record'
    _description = 'A Record For The Learner Skill Plan'

    # Record content
    plan_owner_id = fields.Many2one('res.users', string='Owner of the Plan', readonly=True)
    goal_ids = fields.One2many('skill_development.goal_project','learner_plan_ids', string='Goal')

    sequence = fields.Integer(string="Sequence", default=10)
    skill_id = fields.Many2one('skill_development.skill_record','Skill', readonly=True)
    skill_name = fields.Char(related='skill_id.skill_name', string="Skill Name", store=True, readonly=True)
    motivation = fields.Text(string="My Motivation to Learn")
    endpoint = fields.Date(string="Learning Endpoint")
    msg_2self = fields.Text(string="Message to Myself")

    scribble_note = fields.Html(String='Scribbles', anitize_attributes=False)
    goal_count = fields.Integer(string='View My Goals', compute='_compute_goal_count')

    progress_knowledge = fields.Float('Knowledge', compute="_compute_category_progress", store=True)
    progress_practice = fields.Float('Practice', compute="_compute_category_progress", store=True)
    progress_contribute = fields.Float('Creation & Contribution', compute="_compute_category_progress", store=True)
    overall_progress = fields.Float(string="Overall Progress (%)", compute="_compute_overall_progress", store=True, digits=(6, 2))
    maximum_progress = fields.Integer(string="maximum rate", default=100, store=True)

    is_acquired = fields.Boolean(string="Skill Acquired", default=False)

    skill_status = fields.Char(string="Status",compute='_compute_skill_status', store=False)

    @api.depends('is_acquired')
    def _compute_skill_status(self):
        for rec in self:
            rec.skill_status = 'Acquired' if rec.is_acquired else ''

    @api.depends('goal_ids.goal_progress', 'goal_ids.category')
    def _compute_category_progress(self):
        for learner in self:
            knowledge = practice = cc = 0.0
            for goal in learner.goal_ids:
                if goal.category == 'knowledge':
                    knowledge += goal.goal_progress
                elif goal.category == 'practice':
                    practice += goal.goal_progress
                elif goal.category == 'creation':
                    cc += goal.goal_progress

            learner.progress_knowledge = min(knowledge, 100)
            learner.progress_practice = min(practice, 100)
            learner.progress_contribute = min(cc, 100)

    @api.depends('progress_knowledge', 'progress_practice', 'progress_contribute')
    def _compute_overall_progress(self):
        for learner in self:
            learner.overall_progress = (
                    learner.progress_knowledge * 0.15 +
                    learner.progress_practice * 0.35 +
                    learner.progress_contribute * 0.50
            )

    title = fields.Selection([
        ('seeker', 'Seeker'),
        ('learner', 'Learner'),
        ('skilled', 'Skilled'),
        ('proficient', 'Proficient'),
        ('master', 'Master')
    ], default='seeker', string='Title', compute='_compute_title', store=True, readonly=True)

    @api.depends('overall_progress')
    def _compute_title(self):
        for rec in self:
            if rec.overall_progress >= 80:
                rec.title = 'master'
            elif rec.overall_progress >= 60:
                rec.title = 'proficient'
            elif rec.overall_progress >= 40:
                rec.title = 'skilled'
            elif rec.overall_progress >= 5:
                rec.title = 'learner'
            else:
                rec.title = 'seeker'

    def _compute_goal_count(self):
        for record in self:
            record.goal_count = self.env['skill_development.goal_project'].search_count(
                [('skill_id', '=', record.skill_id.id)])

    def goals_button(self):
        _logger.info("Record ID %s: is_acquired = %s", self.id, self.is_acquired)
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Goals',
            'res_model': 'skill_development.goal_project',
            'view_mode': 'kanban,form',
            'target': 'self',
            'domain': [('skill_id', '=', self.skill_id.id)],
            'context': {'default_skill_id':self.skill_id.id,
                        'default_learner_plan_ids': self.id,
                        'default_is_acquired': self.is_acquired,
                        'create': not self.is_acquired,},
        }

    def popup_help_button(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Help',
            'res_model': 'skill_development.help_popup',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_skill_plan_id': self.id},
        }

    def skill_acquired_button(self):

        for rec in self:
            rec.is_acquired = True

        return {
            'type': 'ir.actions.act_window',
            'name': 'Skill Rating',
            'res_model': 'skill_development.rating',
            'view_mode': 'form',
            'target': 'new',
            'domain': [('learner_plan_record_ids', '=', self.id)],
            'context': {'default_skill_id': self.skill_id.id},
        }

    # @api.model
    # def open_wizard_form(self, context=None):
    #
    #     # get the Learner ID to pass it tp the wizard form in context
    #     employee = self.env['res.users'].search([('id', '=', self.env.uid)], limit=1)
    #     learner_id = employee.id if employee else False
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         # this refers to the wizard form
    #         'res_model': 'skill_plan.form',
    #         'view_mode': 'form',
    #         'name': 'My Skill Plan',
    #         'target': 'new',
    #         'context': {
    #             'default_learner_id': learner_id},  # Pass the learner ID to the wizard form
    #         'default_skill_name': self.skill_name,  # Pass the skill name to the wizard form
    #     }

    # Python constraint to get a unique skill name (the user must create only one plan per skill)
    @api.constrains('skill_id')
    def _check_unique_skill_id(self):
        for record in self:
            # Ensure that the skill name is unique for the current user (record_learner_id)
            if self.search_count([
                ('skill_id', '=', record.skill_id.id),
                ('plan_owner_id', '=', record.plan_owner_id.id)
            ]) > 1:
                raise ValidationError(
                    f"The skill '{record.skill_name}' already exists for this user.\n"
                    f"You can update it by going to your profile and editing the plan record."
                )
    def name_get(self):
        result = []
        for record in self:
            # Return the skill_name as the display name in the learner_skill_id dropdown
            name = record.skill_name or "Unnamed Skill"
            result.append((record.id, name))
        return result

    # Ensures plan_owner_id is automatically set to the current user
    @api.model
    def create(self, vals):
        vals.setdefault('plan_owner_id', self.env.user.id)
        return super(SkillPlan, self).create(vals)

    # For the Smart Goal wizard where a learner can select one of the
    # skills saved in this record to connect the goal to

from odoo import models, fields, api

class PopupHelp(models.TransientModel):  # use TransientModel for wizards/popups
    _name = 'skill_development.help_popup'
    _description = 'Help'

    step = fields.Selection([
        ('page1', 'Overview'),
        ('page2', 'Details')
    ], default='page1', store=True)

    message = fields.Html(string='Help Message', readonly=True)
    tips = fields.Html(string='Tips', readonly=True)
    skill_plan_id = fields.Many2one('skill_development.initial_plan_record', string="Plan")
    overall_progress = fields.Float(related='skill_plan_id.overall_progress', store=True)
    maximum_progress = fields.Integer(string="maximum rate", default=100, store=True)

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        res['message'] = self._get_page1_content()
        return res

    def go_to_page2(self):
        self.write({
            'step': 'page2',
            'message': self._get_page2_content(),
            'tips': self._get_page2_tips()
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'skill_development.help_popup',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def go_to_page1(self):
        self.write({
            'step': 'page1',
            'message': self._get_page1_content(),
            'tips': self._get_page1_tips()
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'skill_development.help_popup',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _get_page1_content(self):
        return """
            <h2>Skill Progress Guide – Page 1</h2>
            <p>Your overall progress is a weighted average of:</p>
            <ul>
                <li><strong>Knowledge:</strong> 15%</li>
                <li><strong>Practice:</strong> 35%</li>
                <li><strong>Contributions & Collaboration:</strong> 50%</li>
            </ul>
            
        """

    def _get_page1_tips(self):
        return """
        <p><strong>Tips:</strong></p>
            <ul>
                <li>Set complete SMART goals</li>
                <li>Add at least two results per goal</li>
                <li>Fill in lessons learned for bonus points</li>
            </ul>
        """

    def _get_page2_tips(self):
        return """
        <h2>Skill Progress Guide – Page 2</h2>
            <p><strong>Title Achievements:</strong></p>
            <ul>
                <li>Seeker: &lt; 5%</li>
                <li>Learner: ≥ 5%</li>
                <li>Skilled: ≥ 40%</li>
                <li>Proficient: ≥ 60%</li>
                <li>Master: ≥ 80%</li>
            </ul>
        """

    def _get_page2_content(self):
        return """
            <p><strong>Category Calculation:</strong></p>
            <ul>
                <li>Each goal is weighted: earlier goals give more %</li>
                <li>Smart goals, completed results, and reflections add bonuses</li>
                <li>Maximum per goal: ~30%</li>
            </ul>
        """




class LearnerProfile(models.Model):
    _inherit = "res.users"

# # Connect the learner to his volunteering record
#     volunteer_record_id = fields.Many2one('volunteer_request.record', string="Volunteering Record ID")
# Connect the learner to his skill plans record (used to save the data in Learner Profile)
    plan_skill_ids = fields.One2many('skill_development.initial_plan_record', 'plan_owner_id', string='Skill Plans')

# Here the data from skill_plan_record are displayed in the Learner Profile
    #record_skill_name = fields.Char(related="plan_skill_ids.skill_name", string="Skill")
    #record_skill_motive = fields.Text(related="plan_skill_ids.motivation" ,string="Motivation to Learn")
    #record_learning_endpoint = fields.Date(related="plan_skill_ids.endpoint" ,string="Learning Endpoint")
    #record_msg_2self = fields.Text(related="plan_skill_ids.msg_2self" ,string="Message to Myself")
