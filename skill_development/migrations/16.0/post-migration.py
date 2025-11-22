def migrate(cr, version):
    old_table = 'skill_development_goal_task'
    new_table = 'skill_development_task'
    old_model = 'skill_development.goal_task'
    new_model = 'skill_development.task'

    # 1. Rename the table
    cr.execute(f"""
        ALTER TABLE {old_table}
        RENAME TO {new_table};
    """)

    # 2. Rename ID sequence if exists
    cr.execute(f"""
        DO $$
        DECLARE
            seq_name text;
        BEGIN
            SELECT pg_get_serial_sequence('{new_table}', 'id') INTO seq_name;
            IF seq_name IS NOT NULL THEN
                EXECUTE 'ALTER SEQUENCE ' || seq_name || ' RENAME TO {new_table}_id_seq';
            END IF;
        END $$;
    """)

    # 3. Fix foreign keys referencing old table
    cr.execute(f"""
        SELECT conname, conrelid::regclass, a.attname
        FROM pg_constraint AS c
        JOIN pg_attribute AS a ON a.attrelid = c.conrelid AND a.attnum = ANY(c.conkey)
        WHERE contype = 'f' AND confrelid = '{old_table}'::regclass;
    """)
    fks = cr.fetchall()
    for constraint_name, table_name, column_name in fks:
        cr.execute(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {constraint_name};")
        cr.execute(f"""
            ALTER TABLE {table_name}
            ADD CONSTRAINT {constraint_name}
            FOREIGN KEY ({column_name}) REFERENCES {new_table}(id) ON DELETE CASCADE;
        """)

    # 4. Rename indexes containing old table name
    cr.execute(f"""
        DO $$
        DECLARE idx record;
        BEGIN
            FOR idx IN
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = '{new_table}' AND indexname LIKE '%{old_table}%'
            LOOP
                EXECUTE 'ALTER INDEX ' || idx.indexname ||
                        ' RENAME TO ' || replace(idx.indexname, '{old_table}', '{new_table}');
            END LOOP;
        END $$;
    """)

    # 5. Ensure old_model exists in ir_model before updating
    cr.execute(f"""
        INSERT INTO ir_model (model, state)
        SELECT '{old_model}', 'base'
        WHERE NOT EXISTS (SELECT 1 FROM ir_model WHERE model='{old_model}');
    """)

    # 6. Update ORM metadata safely
    # 6a. ir_model
    cr.execute(f"""
        UPDATE ir_model
        SET model = '{new_model}'
        WHERE model = '{old_model}';
    """)

    # 6b. ir_model_fields (fields belonging to the model)
    cr.execute(f"""
        UPDATE ir_model_fields
        SET model = '{new_model}'
        WHERE model = '{old_model}';
    """)

    # 6c. ir_model_fields (fields pointing to the model)
    cr.execute(f"""
        UPDATE ir_model_fields
        SET relation = '{new_model}'
        WHERE relation = '{old_model}';
    """)

    # 7. Update ir_model_data (external IDs)
    cr.execute(f"""
        UPDATE ir_model_data
        SET model = '{new_model}'
        WHERE model = '{old_model}';
    """)
