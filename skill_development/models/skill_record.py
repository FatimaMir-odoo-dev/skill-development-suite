# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import models, fields, api, exceptions
from random import randint


class SkillRecord(models.Model):
    _name = "skill_development.skill"
    _description = 'Skill'


    # Skill Record Details:
    skill_name = fields.Char(string='Skill Name', required=True)
    description = fields.Text(string='Skill Description', required=True)
    # learn = fields.Char(string="")
    rating_ids = fields.One2many('skill_development.rating', 'skill_id', stirng="Rating")
    avg_overall_rating = fields.Float('Overall Rating Calculation', compute='_compute_avg_ratings', store=True)
    star_avg_rating = fields.Selection([
        ('0', 'Not Recommended'),
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent'),
    ], store=True, string="Overall Rating", readonly=True)

    star_avg_difficulty = fields.Selection([
        ('0', 'Impossible'),
        ('1', 'Demanding'),
        ('2', 'Challenging'),
        ('3', 'Manageable'),
        ('4', 'Easy'),
        ('5', 'Effortless'),
    ], store=True, string="Overall Difficulty Rating", readonly=True)

    avg_difficulty = fields.Float("Average Difficulty", compute='_compute_avg_ratings', store=True)


    career_path_ids = fields.Many2many('skill_development.career_path',
                                       relation='skill_career_rel',
                                       column1='skill_id',
                                       column2='career_id',
                                       string='Job roles for this skill')

    related_skill_ids = fields.Many2many('skill_development.skill',  relation='skill_related_rel',
                                       column1='skill_id',
                                       column2='related_id',
                                       string='Related Skills',
                                       domain="[('id', '!=', id)]")

    pre_requisites = fields.Text(string="Pre-Requisites")
    prereq_skill_ids = fields.Many2many('skill_development.skill',  relation='skill_prereq_rel',
                                           column1='skill_id',
                                           column2='rprereq_id',
                                           string='Consider Learning First',
                                           domain="[('id', '!=', id)]")

    is_transferable = fields.Boolean(string="This Skill is Transferable")

    @api.depends('rating_ids.usefulness', 'rating_ids.fun2learn', 'rating_ids.difficulty')
    def _compute_avg_ratings(self):
        for skill in self:
            total_usefulness = total_fun = total_difficulty = count = 0

            for rating in skill.rating_ids:
                try:
                    usefulness = int(rating.usefulness or 0)
                    fun = int(rating.fun2learn or 0)
                    difficulty = int(rating.difficulty or 0)

                    # Only count if usefulness, fun, and difficulty are rated above 0
                    if usefulness > 0 and fun > 0 and difficulty > 0:
                        total_usefulness += usefulness
                        total_fun += fun
                        total_difficulty += difficulty
                        count += 1
                except (ValueError, TypeError):
                    continue  # skip invalid entries

            if count:
                avg_rating = round((total_usefulness + total_fun) / (2 * count), 2)
                avg_difficulty = round(total_difficulty / count, 2)
            else:
                avg_rating = 0.0
                avg_difficulty = 0.0

            skill.avg_overall_rating = avg_rating
            skill.avg_difficulty = avg_difficulty

            def to_star(value):
                if 1 <= value < 2:
                    return '1'
                elif 2 <= value < 3:
                    return '2'
                elif 3 <= value < 4:
                    return '3'
                elif 4 <= value < 5:
                    return '4'
                elif value >= 5:
                    return '5'
                else:
                    return '0'  # Not rated

            skill.star_avg_rating = to_star(avg_rating)
            skill.star_avg_difficulty = to_star(avg_difficulty)

    @api.model
    def unlink(self):
        for record in self:
            record.career_path_ids = [(5, 0, 0)]  # Clear the many2many links
        return super(SkillRecord, self).unlink()



    # Check if the Skill Name is unique to prevent duplicated skill creation
    @api.constrains('skill_name')
    def _check_unique_skill_name(self):
        for record in self:
            existing_skill = self.search([('skill_name', '=', record.skill_name), ('id', '!=', record.id)])
            if existing_skill:
                raise exceptions.ValidationError(
                    "A skill with the same name already exists. Please refer back to it or use a different name.")

    # Opens the wizard form for the skill's initial plan.
    # Activated upon clicking the Button: Start Learning

    def action_open_initial_plan_wizard(self, context=None):

        # get the Learner ID to pass it tp the wizard form in context
        # learner = self.env['res.users'].search([('id', '=', self.env.uid)], limit=1)
        # learner_id = learner.id if learner else False

        return {
            'type': 'ir.actions.act_window',
            # this refers to the wizard form
            'res_model': 'skill_development.initial_plan_wizard',
            'view_mode': 'form',
            'name': 'My Skill Plan',
            'target': 'new',
            'context': {
                'default_learner_id': self.env.uid,  # Pass the learner ID to the wizard form
                'default_skill_id': self.id,},  # Pass the skill name to the wizard form
        }

# Get the Skill Name to be used by other records
    def name_get(self):
        result = []
        for record in self:
            name = record.skill_name  # Only use skill_name, without the ID or extra Info
            result.append((record.id, name))
        return result

class CareerPath(models.Model):
    _name = "skill_development.career_path"
    _description = "Skill Career Paths"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Career", required=True)
    description = fields.Text(string="")
    industry_ids = fields.Many2many('skill_development.industry',
                                    relation='career_industry_rel',
                                    column1='career_id',
                                    column2='industry_id',
                                    string="Industries")
    color = fields.Integer(string='Color', default=_get_default_color, help="Color for the career tag")

    @api.model
    def unlink(self):
        for record in self:
            record.industry_ids = [(5, 0, 0)]  # Clear the many2many links
        return super(CareerPath, self).unlink()

class Industry(models.Model):
    _name = "skill_development.industry"
    _description = "Skill Career Paths Industries"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char('Industry Name', required=True, unique=True)  # Unique name field
    color = fields.Integer(string='Color', default=_get_default_color, help="Color for the Industry tag")

    # career_ids = fields.Many2many('skill_development.skill_career', string="")

class Rating(models.Model):
    _name = "skill_development.rating"
    _description = "Skill Rating"

    skill_id = fields.Many2one('skill_development.skill',
                               string="Skill",
                               ondelete='cascade',
                               readonly=True,
                               required=True)

    usefulness = fields.Selection([
        ('0', 'Low'),
        ('1', 'Limited'),
        ('2', 'Basic'),
        ('3', 'Moderate'),
        ('4', 'High'),
        ('5', 'Essential'),
    ],
        default='0', index=True, string="Usefulness", tracking=True)
    fun2learn = fields.Selection([
        ('0', 'Dreadful'),
        ('1', 'Unpleasant'),
        ('2', 'Neutral'),
        ('3', 'Engaging'),
        ('4', 'Fun'),
        ('5', 'Exciting'),
    ],
        default='0', index=True, string="Fun", tracking=True)
    difficulty = fields.Selection([
        ('0', 'Impossible'),
        ('1', 'Demanding'),
        ('2', 'Challenging'),
        ('3', 'Manageable'),
        ('4', 'Easy'),
        ('5', 'Effortless'),
    ],
        default='0', index=True, string="Difficulty", tracking=True)