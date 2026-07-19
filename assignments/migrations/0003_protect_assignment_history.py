import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("assignments", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assignment",
            name="class_room",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="assignments",
                to="academics.classroom",
            ),
        ),
        migrations.AlterField(
            model_name="assignment",
            name="subject",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="assignments",
                to="academics.subject",
            ),
        ),
        migrations.AlterField(
            model_name="assignment",
            name="grading_criteria",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="assignments",
                to="grades.gradingcriteria",
            ),
        ),
    ]
