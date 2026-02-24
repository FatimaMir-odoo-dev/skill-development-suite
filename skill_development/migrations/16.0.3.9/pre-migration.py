"""
Pre-migration script.

This file exists solely for the development stage.
"""

# pylint: disable=invalid-name


def migrate(cr, version):
    pass
    # """Clear old relation tables before ORM upgrade to prevent FK violations."""
    #
    # cr.execute("SELECT to_regclass('public.skill_development_goal_skill_development_tag_rel')")
    # if cr.fetchone()[0]:
    #     # Back up first
    #     cr.execute("""
    #         CREATE TABLE _goal_tag_migration_backup AS
    #         SELECT * FROM skill_development_goal_skill_development_tag_rel
    #         WHERE EXISTS (
    #             SELECT 1 FROM skill_development_goal g
    #             WHERE g.id = skill_development_goal_id
    #         )
    #         AND EXISTS (
    #             SELECT 1 FROM skill_development_tag t
    #             WHERE t.id = skill_development_tag_id
    #         )
    #     """)
    #     # Then empty the old table so ORM doesn't touch it
    #     cr.execute("TRUNCATE skill_development_goal_skill_development_tag_rel")
    #
    # cr.execute("SELECT to_regclass('public.skill_development_tag_skill_development_task_rel')")
    # if cr.fetchone()[0]:
    #     cr.execute("""
    #         CREATE TABLE _task_tag_migration_backup AS
    #         SELECT * FROM skill_development_tag_skill_development_task_rel
    #         WHERE EXISTS (
    #             SELECT 1 FROM skill_development_task t
    #             WHERE t.id = skill_development_task_id
    #         )
    #         AND EXISTS (
    #             SELECT 1 FROM skill_development_tag tg
    #             WHERE tg.id = skill_development_tag_id
    #         )
    #     """)
    #     cr.execute("TRUNCATE skill_development_tag_skill_development_task_rel")
    # """Backup existing goal-tag and task-tag links before relation table rename."""
    #
    # # Goal-tag backup
    # cr.execute("SELECT to_regclass('public.skill_development_tag_skill_development_goal_rel')")
    # if cr.fetchone()[0]:
    #     cr.execute("""
    #                 CREATE TABLE _goal_tag_migration_backup AS
    #                 SELECT *
    #                 FROM skill_development_tag_skill_development_goal_rel
    #             """)
    #
    # # Task-tag backup
    # cr.execute("SELECT to_regclass('public.skill_development_task_skill_development_tag_rel')")
    # if cr.fetchone()[0]:
    #     cr.execute("""
    #                 CREATE TABLE _task_tag_migration_backup AS
    #                 SELECT *
    #                 FROM skill_development_task_skill_development_tag_rel
    #             """)
    # cr.execute("""
    #         SELECT to_regclass(
    #             'public.skill_development_task_skill_development_tag_rel'
    #         )
    #     """)
    # if not cr.fetchone()[0]:
    #     return
    #
    # # new table exists? (created by ORM during upgrade)
    # cr.execute("SELECT to_regclass('public.task_tag_rel')")
    # if not cr.fetchone()[0]:
    #     return
    #
    # cr.execute("""
    #         INSERT INTO task_tag_rel (task_id, tag_id)
    #         SELECT skill_development_task_id, skill_development_tag_id
    #         FROM skill_development_task_skill_development_tag_rel
    #         ON CONFLICT DO NOTHING
    #     """)

    # old_table = 'skill_development_lesson_bank_wizard'
    # new_table = 'skill_development_log_goal_lesson'
    # old_model = 'skill_development.lesson_bank_wizard'
    # new_model = 'skill_development.log_goal_lesson'
    #
    # # Check if old table exists
    # cr.execute("""
    #     SELECT EXISTS (
    #         SELECT FROM pg_tables
    #         WHERE schemaname = 'public'
    #         AND tablename = %s
    #     );
    # """, (old_table,))
    #
    # old_exists = cr.fetchone()[0]
    #
    # # Check if new table exists
    # cr.execute("""
    #     SELECT EXISTS (
    #         SELECT FROM pg_tables
    #         WHERE schemaname = 'public'
    #         AND tablename = %s
    #     );
    # """, (new_table,))
    #
    # new_exists = cr.fetchone()[0]
    #
    # if old_exists and not new_exists:
    #     # Rename table
    #     cr.execute(f"ALTER TABLE public.{old_table} RENAME TO {new_table};")
    #
    #     # Rename sequence
    #     cr.execute(f"""
    #         ALTER SEQUENCE IF EXISTS public.{old_table}_id_seq
    #         RENAME TO {new_table}_id_seq;
    #     """)
    #
    #     # IMPORTANT: Rename columns in many-to-many relation tables
    #     cr.execute("""
    #                 SELECT table_name, column_name
    #                 FROM information_schema.columns
    #                 WHERE table_schema = 'public'
    #                     AND table_name LIKE 'skill_development%'
    #                     AND column_name = 'skill_development_goal_tag_id';
    #             """)
    #
    #     relation_tables = cr.fetchall()
    #     for table_name, column_name in relation_tables:
    #         cr.execute(f"""
    #                     ALTER TABLE {table_name}
    #                     RENAME COLUMN skill_development_goal_tag_id TO skill_development_tag_id;
    #                 """)
    #
    # # Get old model ID if it exists
    # cr.execute("SELECT id FROM ir_model WHERE model = %s", (old_model,))
    # old_model_record = cr.fetchone()
    # old_model_id = old_model_record[0] if old_model_record else None
    #
    # # Check if new model already exists
    # cr.execute("SELECT id FROM ir_model WHERE model = %s", (new_model,))
    # new_model_exists = cr.fetchone()
    #
    # if new_model_exists:
    #     # New model exists, delete references to old model
    #     if old_model_id:
    #         cr.execute("DELETE FROM ir_model_constraint WHERE model = %s;", (old_model_id,))
    #     cr.execute("DELETE FROM ir_model_fields WHERE model = %s;", (old_model,))
    #     cr.execute("DELETE FROM ir_model_data WHERE model = %s;", (old_model,))
    #     cr.execute("DELETE FROM ir_model WHERE model = %s;", (old_model,))
    # else:
    #     # New model doesn't exist, safe to UPDATE
    #     cr.execute("UPDATE ir_model SET model = %s WHERE model = %s;", (new_model, old_model))
    #     cr.execute("UPDATE ir_model_fields SET model = %s WHERE model = %s;", (new_model, old_model))
    #     cr.execute("UPDATE ir_model_data SET model = %s WHERE model = %s;", (new_model, old_model))
    #     # ir_model_constraint.model is an integer FK, no update needed
    #
    # # These can always be updated
    # cr.execute("UPDATE ir_model_fields SET relation = %s WHERE relation = %s;", (new_model, old_model))
    # cr.execute("UPDATE ir_ui_view SET model = %s WHERE model = %s;", (new_model, old_model))
    # cr.execute("UPDATE ir_act_window SET res_model = %s WHERE res_model = %s;", (new_model, old_model))
