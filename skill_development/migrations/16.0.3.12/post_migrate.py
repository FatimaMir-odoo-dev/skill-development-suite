def migrate(cr, version):
    pass
    # """Restore goal-tag and task-tag links into the new named relation tables."""
    #
    # # Clean any orphaned rows the ORM may have copied during upgrade
    # cr.execute("SELECT to_regclass('public.goal_tag_rel')")
    # if cr.fetchone()[0]:
    #     cr.execute("""
    #         DELETE FROM goal_tag_rel
    #         WHERE NOT EXISTS (
    #             SELECT 1 FROM skill_development_goal g WHERE g.id = goal_tag_rel.goal_id
    #         )
    #         OR NOT EXISTS (
    #             SELECT 1 FROM skill_development_tag t WHERE t.id = goal_tag_rel.tag_id
    #         )
    #     """)
    #
    # # Goal-tag restore from backup
    # cr.execute("SELECT to_regclass('public._goal_tag_migration_backup')")
    # if cr.fetchone()[0]:
    #     cr.execute("SELECT to_regclass('public.goal_tag_rel')")
    #     if cr.fetchone()[0]:
    #         cr.execute("""
    #             INSERT INTO goal_tag_rel (goal_id, tag_id)
    #             SELECT skill_development_goal_id, skill_development_tag_id
    #             FROM _goal_tag_migration_backup
    #             ON CONFLICT DO NOTHING
    #         """)
    #     cr.execute("DROP TABLE _goal_tag_migration_backup")
    #
    # # Task-tag restore from backup
    # cr.execute("SELECT to_regclass('public._task_tag_migration_backup')")
    # if cr.fetchone()[0]:
    #     cr.execute("SELECT to_regclass('public.task_tag_rel')")
    #     if cr.fetchone()[0]:
    #         cr.execute("""
    #             INSERT INTO task_tag_rel (task_id, tag_id)
    #             SELECT skill_development_task_id, skill_development_tag_id
    #             FROM _task_tag_migration_backup
    #             ON CONFLICT DO NOTHING
    #         """)
    #     cr.execute("DROP TABLE _task_tag_migration_backup")
