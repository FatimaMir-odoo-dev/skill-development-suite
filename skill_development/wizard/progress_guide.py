# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

from odoo import api, fields, models


class ProgressGuide(models.TransientModel):
    """
    Skill Progress Help Wizard.

    Interactive help dialog that explains how skill progress,
    categories, and titles are calculated for a skill growth plan.
    """

    _name = 'skill_development.progress_guide'
    _description = 'Help / Skill Growth Guide'

    step = fields.Selection([
        ('page1', 'Overview'),
        ('page2', 'Details')
    ], default='page1', store=True)

    skill_plan_id = fields.Many2one('skill_development.growth_tracker', string="Plan")

    message = fields.Html(string='Help Message', readonly=True)
    tips = fields.Html(string='Tips', readonly=True)
    title = fields.Selection([
        ('seeker', 'Seeker'),
        ('learner', 'Learner'),
        ('skilled', 'Skilled'),
        ('proficient', 'Proficient'),
        ('master', 'Master')
    ], default='seeker', string='Title', store=True, readonly=True)
    overall_progress = fields.Float(store=True)
    maximum_progress = fields.Integer(string="maximum rate", default=100, store=True)

    @api.model
    def default_get(self, fields):# pylint: disable=redefined-outer-name
        """Initialize the wizard with the first help page content upon opening it."""

        res = super().default_get(fields)
        res['message'] = self._get_page1_content()
        res['tips'] = self._get_page1_tips()
        return res

    # 6. NAVIGATION METHODS
# ---------------------------------------------------------
    def go_to_page2(self):
        """Switch the wizard to the next page of the help guide."""

        self.write({
            'step': 'page2',
            'message': self._get_page2_content(),
            'tips': self._get_page2_tips()
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'skill_development.progress_guide',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def go_to_page1(self):
        """Return the wizard to the first help page."""

        self.write({
            'step': 'page1',
            'message': self._get_page1_content(),
            'tips': self._get_page1_tips()
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'skill_development.progress_guide',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    # 6. HELP CONTENT METHODS
# ---------------------------------------------------------
    def _get_page1_content(self):
        """ First page contents
        Explains overall progress and how category weights work. """

        return """
    <div class="container">
        <h1 class="text-center text-4xl font-bold text-gray-900 mb-6">Welcome to Your Skill Growth Journey!</h1>

        <p class="text-lg text-gray-700 mb-8">
            This guide will help you understand how your skill progress is calculated and how to grow effectively.
        </p>

        <h2 class="text-3xl font-semibold text-gray-800 mb-4">What is Overall Progress?</h2>

        <p class="text-gray-700 mb-4">
            Your overall progress shows how much you've developed a skill. It's based on three key areas:
        </p>

        <ul class="list-disc ml-6 mb-6 text-gray-700">
            <li><strong class="highlight">Knowledge (15%):</strong> What you learn (e.g., reading, courses).</li>
            <li><strong class="highlight">Practice (35%):</strong> What you do (e.g., exercises, projects).</li>
            <li><strong class="highlight">Connect &amp; Contribute (50%):</strong> What you share and teach (e.g., helping others, collaborating).</li> # noqa: E501
        </ul>

        <p class="text-gray-700 mb-4">
            Each area has a score out of 100%. Your overall progress is calculated like this:
        </p>

        <div class="calculation-box bg-gray-200 p-4 rounded-lg mb-6">
            <code class="text-gray-800">
                Overall Progress = (Knowledge % x 0.15) + (Practice % x 0.35) + (Connect &amp; Contribute % x 0.50)
            </code>
        </div>

        <p class="text-gray-700">
            As you can see, <strong class="highlight">Practice</strong> and <strong class="highlight">Connect &amp; Contribute</strong> are worth more, because applying and sharing your skills is the best way to learn! # noqa: E501
        </p>
    </div>

        """

    def _get_page1_tips(self):
        """ First page contents
        Provides learning and goal-setting recommendations."""

        return """
        <div class="container">
        <p class="text-lg text-gray-700 mb-8">
            As you can see, <strong class="highlight">Practice</strong> and <strong class="highlight">Connect &amp; Contribute</strong> are worth more, because applying and sharing your skills is the best way to learn!
        </p>

        <h2 class="text-3xl font-semibold text-gray-800 mb-4">How to Grow Your Skills Effectively</h2>

        <p class="text-gray-700 mb-4">
            Follow these tips to maximize your skill growth:
        </p>

        <ul class="list-disc ml-6 mb-6 text-gray-700">
            <li><strong class="highlight">Start Strong:</strong> Aim to complete your first goal in each category. The first goal gives you the biggest boost.</li>
            <li><strong class="highlight">Set SMART Goals:</strong> Make your goals <strong class="highlight">S</strong>pecific, <strong class="highlight">M</strong>easurable, <strong class="highlight">A</strong>chievable, <strong class="highlight">R</strong>elevant, and <strong class="highlight">T</strong>ime-bound. This helps you stay focused and track your progress.</li>
            <li><strong class="highlight">Reflect on What You Learn:</strong> When you complete a goal, take the time to fill out the reflection questions. Reflecting earns you extra progress!</li>
            <li><strong class="highlight">Mix It Up:</strong> Diversify your goals. Try different goals in each category to develop a well-rounded skillset.</li>
            <li><strong class="highlight">Help Others:</strong> Sharing your knowledge by teaching or working with others is a great way to deepen your understanding and accelerate your progress.</li>
        </ul>
    </div>
        """

    def _get_page2_tips(self):
        """ Second page contents
        Describes category scoring, bonuses, and limits."""

        return """
        <h2 class="text-3xl font-semibold text-gray-800 mb-4">Your Skill Titles</h2>

        <p class="text-lg text-gray-700 mb-6">
            As your overall progress increases, you'll unlock new skill titles:
        </p>

        <table>
            <thead>
                <tr>
                    <th>Progress</th>
                    <th>Title</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>0 – 4%</td>
                    <td>Seeker</td>
                </tr>
                <tr>
                    <td>5 – 39%</td>
                    <td>Learner</td>
                </tr>
                <tr>
                    <td>40 – 59%</td>
                    <td>Skilled</td>
                </tr>
                <tr>
                    <td>60 – 79%</td>
                    <td>Proficient</td>
                </tr>
                <tr>
                    <td>80 – 100%</td>
                    <td>Master</td>
                </tr>
            </tbody>
        </table>

        <div class="bonus-box">
            <p class="text-gray-700">
                <strong>So, every action you take moves you forward!</strong>
            </p>
        </div>
        """

    # flake8: noqa: E501
    def _get_page2_content(self):
        """ Second page content
        Shows how overall progress maps to learner titles."""

        return """
            <h2 class="text-3xl font-semibold text-gray-800 mb-4">Understanding Your Progress</h2>

        <p class="text-lg text-gray-700 mb-8">
            This page explains how progress is calculated in each category and how your overall progress translates into skill titles. # noqa: E501
        </p>

        <h2 class="text-3xl font-semibold text-gray-800 mb-4">Progress by Category</h2>

        <p class="text-gray-700 mb-4">
            Each time you complete a goal, you earn progress in that category. Here's how it works:
        </p>

        <ul class="list-disc ml-6 mb-6 text-gray-700">
            <li><strong class="highlight">Base Value:</strong> Your first goal = 20% progress. Each following goal adds 2% less (e.g., 2nd goal = 18%, 3rd goal = 16%, and so on).</li> # noqa: E501
            <li><strong class="highlight">SMART Goal Bonus:</strong> Get up to +5% extra progress if your goal is <strong class="highlight">S</strong>pecific, <strong class="highlight">M</strong>easurable, <strong class="highlight">A</strong>chievable, <strong class="highlight">R</strong>elevant, and <strong class="highlight">T</strong>ime-bound.</li> # noqa: E501
            <li><strong class="highlight">Reflection Bonus:</strong> Get +5% extra progress if you answer all 3 reflection questions when you complete a goal.</li> # noqa: E501
            <li><strong class="highlight">"Done" Requirement Penalty:</strong> Lose -1% if you mark fewer than 2 expected results as "Done" for a goal.</li> # noqa: E501
            <li><strong class="highlight">Category Limit:</strong> You can earn a maximum of 100% progress in each of the **Knowledge**, **Practice**, and **Connect &amp; Contribute** categories.</li> # noqa: E501
        </ul>
        """
