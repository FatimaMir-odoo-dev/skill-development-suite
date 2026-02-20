def migrate(cr, version):
    cr.execute("DROP TABLE IF EXISTS goal_tag_rel")
