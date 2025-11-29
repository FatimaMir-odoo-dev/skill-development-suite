# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).
from email.policy import default

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

from sass import and_join

_logger = logging.getLogger(__name__)


class GrowthTracker(models.Model):
    _name = 'skill_development.growth_tracker'
    _description = 'A Record For The Learner Skill Plan'

    # Record content
    plan_owner_id = fields.Many2one('res.users', string='Owner of the Plan', readonly=True)
    goal_ids = fields.One2many('skill_development.goal', 'learner_plan_ids', string='Goal')

    sequence = fields.Integer(string="Sequence", default=10)
    skill_id = fields.Many2one('skill_development.skill', 'Skill', readonly=True)
    skill_name = fields.Char(related='skill_id.skill_name', string="Skill Name", store=True, readonly=True)
    motivation = fields.Text(string="My Motivation to Learn")
    motivation_short = fields.Html(string="Motivation Preview", compute="_compute_motivation_short", sanitize_attributes=False)
    endpoint = fields.Date(string="Learning Endpoint")
    msg_2self = fields.Text(string="Message to Myself")

    scribble_note = fields.Html(string='Scribbles', sanitize_attributes=False)
    goal_count = fields.Integer(string='View My Goals', compute='_compute_goal_count')

    progress_knowledge = fields.Float('Knowledge', compute="_compute_category_progress", store=True,
                                      help="Knowledge category is about increasing your understanding of the skill, with reading articles, watching videos, taking courses, and studying relevant materials.")
    progress_practice = fields.Float('Practice', compute="_compute_category_progress", store=True,
                                     help="The Practice category involves applying the skill through hands-on activities, such as exercises, personal projects, simulations, and practical application.")
    progress_contribute = fields.Float('Creation & Contribution', compute="_compute_category_progress", store=True,
                                       help="Creation & Contribution involves sharing and benefiting from your knowledge: teaching, mentoring, working for return and publishing projects.")
    overall_progress = fields.Float(string="Overall Progress (%)", compute="_compute_overall_progress", store=True,
                                    digits=(6, 2))
    maximum_progress = fields.Integer(string="maximum rate", default=100, store=True)

    is_acquired = fields.Boolean(string="Skill Acquired", store=True)

    skill_status = fields.Char(string="Status", compute='_compute_skill_status', store=False)
    active = fields.Boolean(default=True)

    @api.depends('motivation')
    def _compute_motivation_short(self):
        for record in self:
            record.motivation_short = (record.motivation[:120] + '...') if record.motivation and len(
                record.motivation) > 50 else record.motivation

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
            record.goal_count = self.env['skill_development.goal'].search_count(
                [('skill_id', '=', record.skill_id.id)])

    def goals_button(self):
        _logger.info("plan_owner_id %s: current user id = %s", self.plan_owner_id, self._uid)
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Goals',
            'res_model': 'skill_development.goal',
            'view_mode': 'kanban,form',
            'target': 'self',
            'domain': [('skill_id', '=', self.skill_id.id)],
            'context': {'default_skill_id': self.skill_id.id,
                        'default_learner_plan_ids': self.id,
                        'create': not self.is_acquired, },
        }

    def popup_help_button(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Help',
            'res_model': 'skill_development.progress_guide',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_skill_plan_id': self.id,
                        'default_overall_progress': self.overall_progress,
                        'default_title': self.title, },
        }

    def action_archive_plan(self):
        self.active = False
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Plan Archived'),
                'message': _('The skill "%s" has been archived, view by filtering with (Active is No).' % self.skill_id.skill_name),
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_delete_plan(self):
        skill = self.browse(self.id)
        if not skill.exists():
            raise UserError(_("The skill you're trying to delete does not exist."))
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Confirm Deletion'),
            'res_model': 'skill_development.delete_progress',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_plan_id': self.id,
            },
        }

    def skill_acquired_button(self):

        for rec in self:
            rec.is_acquired = True

        return {
            'type': 'ir.actions.act_window',
            'name': 'Skill Rating',
            'res_model': 'skill_development.skill_rating',
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
        return super(GrowthTracker, self).create(vals)

    # For the Smart Goal wizard where a learner can select one of the
    # skills saved in this record to connect the goal to

#
# from odoo import models, fields, api




class LearnerProfile(models.Model):
    _inherit = "res.users"


    plan_skill_ids = fields.One2many('skill_development.growth_tracker', 'plan_owner_id', string='Skill Plans')

    # # Connect the learner to his volunteering record
    #     volunteer_record_id = fields.Many2one('volunteer_request.record', string="Volunteering Record ID")
    # Connect the learner to his skill plans record (used to save the data in Learner Profile)

# Here the data from skill_plan_record are displayed in the Learner Profile
# record_skill_name = fields.Char(related="plan_skill_ids.skill_name", string="Skill")
# record_skill_motive = fields.Text(related="plan_skill_ids.motivation" ,string="Motivation to Learn")
# record_learning_endpoint = fields.Date(related="plan_skill_ids.endpoint" ,string="Learning Endpoint")
# record_msg_2self = fields.Text(related="plan_skill_ids.msg_2self" ,string="Message to Myself")
