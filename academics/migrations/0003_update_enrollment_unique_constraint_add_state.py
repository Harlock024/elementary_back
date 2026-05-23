from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0002_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE enrollments
                        DROP CONSTRAINT IF EXISTS enrollments_student_id_period_group_id_b9d71eb6_uniq;

                        ALTER TABLE enrollments
                        ADD CONSTRAINT enrollments_student_id_period_group_id_state_uniq
                        UNIQUE (student_id, period, group_id, state);
                    """,
                    reverse_sql="""
                        ALTER TABLE enrollments
                        DROP CONSTRAINT IF EXISTS enrollments_student_id_period_group_id_state_uniq;

                        ALTER TABLE enrollments
                        ADD CONSTRAINT enrollments_student_id_period_group_id_b9d71eb6_uniq
                        UNIQUE (student_id, period, group_id);
                    """,
                ),
            ],
            state_operations=[
                migrations.AlterUniqueTogether(
                    name='enrollment',
                    unique_together=set(),
                ),
                migrations.AlterField(
                    model_name='enrollment',
                    name='state',
                    field=models.CharField(default='activo', max_length=20),
                ),
                migrations.AlterUniqueTogether(
                    name='enrollment',
                    unique_together={('student', 'period', 'group', 'state')},
                ),
            ],
        ),
    ]
