from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academics", "0008_default_active_period"),
        ("grades", "0003_protect_grading_history"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="studentgrade",
            constraint=models.UniqueConstraint(
                fields=("student", "assignment"),
                name="uniq_student_assignment_grade",
            ),
        ),
    ]
