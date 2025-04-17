{
    'name': 'Skill Development',
    'version': '16.0.2.0',
   'summary': 'Personalized learning plans, course enrollment, and event participation to enhance skills',
    'description': 'Description',
    'category': 'Skill Development',
    'author': 'FATIMA',
    # 'license': 'License',
    'depends': ['base', 'hr' ,'web_responsive', 'project'],
    'data': [
        'security/skill_development_groups.xml',
        'security/ir.model.access.csv',
        'views/skill_record_views.xml',
        'views/skill_development_menu.xml',
        'wizard/skill_initial_plan_wizard_views.xml',
        'views/skill_initial_plan_record_views.xml',
        'views/smart_goal_plan_record_views.xml',
        # 'wizard/smart_goal_form_wizard_views.xml',
             ],
    # 'demo': ['Demo'],
    'installable': True,
    'auto_install': True
}
