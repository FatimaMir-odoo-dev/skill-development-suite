# Copyright (C) 2024 FatimaMir-odoo-dev
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

{
    'name': 'Skill Development',
    'version': '16.0.2.0',
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
    'depends': ['base', 'hr' ,'web_responsive', 'project'],
    'data': [
        'security/skill_development_groups.xml',
        'security/ir.model.access.csv',
        'views/skill_record_views.xml',
        'views/skill_development_menu.xml',
        'wizard/skill_initial_plan_wizard_views.xml',
        'views/skill_initial_plan_record_views.xml',
        'views/smart_goal_plan_record_views.xml',
        'views/skill_growth_record_views.xml',
        'views/goal_views.xml',
        # 'wizard/smart_goal_form_wizard_views.xml',
             ],
    # 'demo': ['demo/demo.xml'],
    'installable': True,
    'auto_install': False,
    'application': True
}
