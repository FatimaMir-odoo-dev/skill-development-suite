def migrate(cr, version):
    # pass
    old_table = 'skill_development_initial_plan_record'
    new_table = 'skill_development_growth_tracker'
    old_model = 'skill_development.initial_plan_record'
    new_model = 'skill_development.growth_tracker'

    # Check if old table exists
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename = %s
        );
    """, (old_table,))

    old_exists = cr.fetchone()[0]

    # Check if new table exists
    cr.execute("""
        SELECT EXISTS (
            SELECT FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename = %s
        );
    """, (new_table,))

    new_exists = cr.fetchone()[0]

    if old_exists and not new_exists:
        # Rename table
        cr.execute(f"ALTER TABLE public.{old_table} RENAME TO {new_table};")

        # Rename sequence
        cr.execute(f"""
            ALTER SEQUENCE IF EXISTS public.{old_table}_id_seq
            RENAME TO {new_table}_id_seq;
        """)

        # IMPORTANT: Rename columns in many-to-many relation tables
        cr.execute("""
                    SELECT table_name, column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                        AND table_name LIKE 'skill_development%'
                        AND column_name = 'skill_development_goal_tag_id';
                """)

        relation_tables = cr.fetchall()
        for table_name, column_name in relation_tables:
            cr.execute(f"""
                        ALTER TABLE {table_name}
                        RENAME COLUMN skill_development_goal_tag_id TO skill_development_tag_id;
                    """)

    # Get old model ID if it exists
    cr.execute("SELECT id FROM ir_model WHERE model = %s", (old_model,))
    old_model_record = cr.fetchone()
    old_model_id = old_model_record[0] if old_model_record else None

    # Check if new model already exists
    cr.execute("SELECT id FROM ir_model WHERE model = %s", (new_model,))
    new_model_exists = cr.fetchone()

    if new_model_exists:
        # New model exists, delete references to old model
        if old_model_id:
            cr.execute("DELETE FROM ir_model_constraint WHERE model = %s;", (old_model_id,))
        cr.execute("DELETE FROM ir_model_fields WHERE model = %s;", (old_model,))
        cr.execute("DELETE FROM ir_model_data WHERE model = %s;", (old_model,))
        cr.execute("DELETE FROM ir_model WHERE model = %s;", (old_model,))
    else:
        # New model doesn't exist, safe to UPDATE
        cr.execute("UPDATE ir_model SET model = %s WHERE model = %s;", (new_model, old_model))
        cr.execute("UPDATE ir_model_fields SET model = %s WHERE model = %s;", (new_model, old_model))
        cr.execute("UPDATE ir_model_data SET model = %s WHERE model = %s;", (new_model, old_model))
        # ir_model_constraint.model is an integer FK, no update needed

    # These can always be updated
    cr.execute("UPDATE ir_model_fields SET relation = %s WHERE relation = %s;", (new_model, old_model))
    cr.execute("UPDATE ir_ui_view SET model = %s WHERE model = %s;", (new_model, old_model))
    cr.execute("UPDATE ir_act_window SET res_model = %s WHERE res_model = %s;", (new_model, old_model))