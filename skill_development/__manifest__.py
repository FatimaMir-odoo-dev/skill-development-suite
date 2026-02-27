# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

# pylint: disable=pointless-statement,missing-module-docstring
{
    'name': 'Skill Development',
    'version': '16.0.3.10',
    'summary': 'Personalized learning plans for skill development.',
    'description': """
        It's the core of the Skill Development Suite.
        It enables learners to create personalized skill growth plans using SMART goals, tasks and resources.
        Originally developed for the IEEE Student Branch at Al-Neelain University,
        it is fully adaptable for any learning-focused organization.
        """,
    'category': 'Human Resources',
    'author': 'FatimaMir-odoo-dev',
    'license': 'LGPL-3',
    'depends': ['base', 'hr'],
    'data': [
        'security/skill_development_groups.xml',
        'security/ir.model.access.csv',
        'security/security_groups.xml',
        'views/skill_views.xml',
        'wizard/create_initial_plan_view.xml',
        'views/growth_tracker_views.xml',
        'views/skill_development_menu.xml',
        'views/goal_views.xml',
        'wizard/log_goal_lesson_view.xml',
        'wizard/delete_progress_view.xml',
        'wizard/progress_guide_view.xml',
    ],
    # 'demo': ['demo/demo.xml'],
    'installable': True,
    'auto_install': False,
    'application': True
}
