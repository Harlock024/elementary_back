import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("grades", "0002_alter_gradingcriteria_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gradingcriteria",
            name="class_room",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="grading_criteria",
                to="academics.classroom",
            ),
        ),
        migrations.AlterField(
            model_name="studentgrade",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="grades",
                to="students.student",
            ),
        ),
        migrations.AlterField(
            model_name="studentgrade",
            name="class_room",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="grades",
                to="academics.classroom",
            ),
        ),
        migrations.AlterField(
            model_name="studentgrade",
            name="subject",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="grades",
                to="academics.subject",
            ),
        ),
        migrations.AlterField(
            model_name="studentgrade",
            name="assignment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="grades",
                to="assignments.assignment",
            ),
        ),
    ]
