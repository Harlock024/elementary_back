from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0003_update_enrollment_unique_constraint_add_state'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE enrollments
                            DROP CONSTRAINT IF EXISTS enrollments_student_id_period_group_id_state_uniq;
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM pg_class
                                WHERE relname = 'enrollments_student_id_period_group_id_b9d71eb6_uniq'
                            ) THEN
                                ALTER TABLE enrollments
                                    ADD CONSTRAINT enrollments_student_id_period_group_id_b9d71eb6_uniq
                                    UNIQUE (student_id, period, group_id);
                            END IF;
                        END $$;
                    """,
                    reverse_sql="""
                        ALTER TABLE enrollments
                            DROP CONSTRAINT IF EXISTS enrollments_student_id_period_group_id_b9d71eb6_uniq;
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM pg_class
                                WHERE relname = 'enrollments_student_id_period_group_id_state_uniq'
                            ) THEN
                                ALTER TABLE enrollments
                                    ADD CONSTRAINT enrollments_student_id_period_group_id_state_uniq
                                    UNIQUE (student_id, period, group_id, state);
                            END IF;
                        END $$;
                    """,
                ),
            ],
            state_operations=[
                migrations.AlterUniqueTogether(
                    name='enrollment',
                    unique_together={('student', 'period', 'group')},
                ),
            ],
        ),
    ]
