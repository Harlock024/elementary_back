import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("attendance", "0002_alter_catalogtypeatendance_code_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="attendance",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="attendances",
                to="students.student",
            ),
        ),
        migrations.AlterField(
            model_name="attendance",
            name="class_room",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="attendances",
                to="academics.classroom",
            ),
        ),
    ]
