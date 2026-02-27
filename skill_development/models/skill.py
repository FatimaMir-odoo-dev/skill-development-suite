# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from random import randint

from odoo import api, fields, models


class Skill(models.Model):
    """ ReDoc
        Skill definition model.

        Represents a learnable skill with descriptive information,
        related skills, associated career paths, and aggregated
        community ratings for usefulness and difficulty.
        """

    _name = "skill_development.skill"
    _description = 'Skill'
    _rec_name = 'skill_name'

    # BASIC FIELDS (IDENTITY + DESCRIPTION)
    # ________________________________________
    skill_name = fields.Char(string='Skill Name', required=True)
    description = fields.Text(string='Skill Description', required=True)
    pre_requisites = fields.Text(string="Pre-Requisites")
    # ________________________________________

    # RELATIONAL FIELDS
    # ________________________________________
    rating_ids = fields.One2many('skill_development.skill_rating',
                                 'skill_id',
                                 string="Ratings")

    career_path_ids = fields.Many2many('skill_development.skill_career',
                                       relation='skill_career_rel',
                                       column1='skill_id',
                                       column2='career_id',
                                       string='Job Roles for this Skill')

    related_skill_ids = fields.Many2many('skill_development.skill',
                                         relation='skill_related_rel',
                                         column1='skill_id',
                                         column2='related_id',
                                         string='Related Skills',
                                         domain="[('id', '!=', id)]")

    prereq_skill_ids = fields.Many2many('skill_development.skill',
                                        relation='skill_prereq_rel',
                                        column1='skill_id',
                                        column2='prereq_id',
                                        string='Consider Learning First',
                                        domain="[('id', '!=', id)]")

    # STAR RATING FIELDS (READONLY OUTPUTS)
    # ________________________________________
    star_avg_rating = fields.Selection([
        ('0', 'Not Recommended'),
        ('1', 'Poor'),
        ('2', 'Fair'),
        ('3', 'Good'),
        ('4', 'Very Good'),
        ('5', 'Excellent'), ],
        store=True,
        string="Overall Rating",
        readonly=True,
        compute='_compute_avg_ratings')

    star_avg_difficulty = fields.Selection([
        ('0', 'Effortless'),
        ('1', 'Easy'),
        ('2', 'Manageable'),
        ('3', 'Challenging'),
        ('4', 'Demanding'),
        ('5', 'Impossible'), ],
        store=True,
        string="Overall Difficulty Rating",
        readonly=True,
        compute='_compute_avg_ratings')
    # ________________________________________

    # FLAGS
    # ________________________________________
    is_transferable = fields.Boolean(string="This Skill is Transferable")

    # The constraint ensures no duplicate skills are added to the Skill Catalog.
    # Triggered when creating or updating a new skill record.
    _sql_constraints = [
        ('unique_skill_name', 'unique(skill_name)',
         'A skill with the same name already exists. Please refer back to it or use a different name.')
    ]

    @staticmethod
    def _to_star(value):
        thresholds = [5, 4, 3, 2, 1]
        for threshold in thresholds:
            if value >= threshold:
                return str(threshold)
        return '0'

    @api.depends('rating_ids.usefulness', 'rating_ids.fun2learn', 'rating_ids.difficulty')
    def _compute_avg_ratings(self):
        """
            Compute average rating and difficulty for the skill.

            Aggregates valid user ratings to calculate:
            - Overall rating (based on usefulness and fun)
            - Average difficulty
            - Star-based values used for UI display on the skill card
            """
        for skill in self:
            total_usefulness = total_fun = total_difficulty = count = 0

            for rating in skill.rating_ids:
                usefulness = int(rating.usefulness)
                fun = int(rating.fun2learn)
                difficulty = int(rating.difficulty)

                # Only count if usefulness, fun, and difficulty are rated above 0
                if usefulness > 0 and fun > 0 and difficulty > 0:
                    total_usefulness += usefulness
                    total_fun += fun
                    total_difficulty += difficulty
                    count += 1

            if count:
                avg_rating = round((total_usefulness + total_fun) / (2 * count), 2)
                avg_difficulty = round(total_difficulty / count, 2)
            else:
                avg_rating = 0.0
                avg_difficulty = 0.0

            skill.star_avg_rating = self._to_star(avg_rating)
            skill.star_avg_difficulty = self._to_star(avg_difficulty)

    # def unlink(self):
    #     for record in self:
    #         record.career_path_ids = [(5, 0, 0)]  # Clear the many2many links
    #     return super(Skill, self).unlink()

    # Opens the wizard form for the skill's initial plan.
    # Activated upon clicking the Button: Start Learning

    def action_open_initial_plan_wizard(self):
        """Opens a pop-up window to create an initial development plan for a new skill."""

        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            # this refers to the wizard form
            'res_model': 'skill_development.create_initial_plan',
            'view_mode': 'form',
            'name': 'My Skill Plan',
            'target': 'new',
            'context': {
                'default_learner_id': self.env.user.id,
                'default_skill_id': self.id, },
        }


class SkillCareer(models.Model):
    """ Represents a career or job role that can be associated with multiple skills
     and categorized by industry."""

    _name = "skill_development.skill_career"
    _description = "Skill Career Paths"

    name = fields.Char(string="Career", required=True)
    description = fields.Text(string="")
    color = fields.Integer(
        string='Color',
        default=lambda self: randint(1, 11),
        help="Color used in Kanban or labels.")
    industry_ids = fields.Many2many('skill_development.career_industry',
                                    relation='career_industry_rel',
                                    column1='career_id',
                                    column2='industry_id',
                                    string="Industries")


class CareerIndustry(models.Model):
    """
       Represents different industries used to classify
       different career paths.
       """

    _name = "skill_development.career_industry"
    _description = "Skill Career Paths Industries"

    # Ensures no industry name is repeated in the Skill Catalog - section: Job Roles for this Skill
    _sql_constraints = [
        ('tag_name_unique', 'unique(name)', 'An industry with this name already exists.')
    ]

    name = fields.Char('Industry Name', required=True)  # Unique name field
    color = fields.Integer(
        string='Color',
        default=lambda self: randint(1, 11),
        help="Color for the Industry tag")

    # career_ids = fields.Many2many('skill_development.skill_career', string="")


class SkillRating(models.Model):
    """
       Stores user evaluations of a skill after acquiring it based on:
       - How useful it was for them.
       - How much enjoyment they got out of learning it.
       - Its level of difficulty.

       These ratings are used to compute the overall skill rating metric
       displayed on the skill record.
       """

    _name = "skill_development.skill_rating"
    _description = "Skill Rating"
    _rec_name = 'skill_id'

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
        ('5', 'Essential'), ],
        default='0', index=True, string="Usefulness")

    fun2learn = fields.Selection([
        ('0', 'Dreadful'),
        ('1', 'Unpleasant'),
        ('2', 'Neutral'),
        ('3', 'Engaging'),
        ('4', 'Fun'),
        ('5', 'Exciting'), ],
        default='0', index=True, string="Fun")

    difficulty = fields.Selection([
        ('0', 'Effortless'),
        ('1', 'Easy'),
        ('2', 'Manageable'),
        ('3', 'Challenging'),
        ('4', 'Demanding'),
        ('5', 'Impossible'), ],
        default='0', index=True, string="Difficulty")
