def migrate(cr, version):
    cr.execute("DROP TABLE IF EXISTS skill_development_task_skill_development_tag_rel")
