import django.db.models.deletion
from django.db import migrations, models

import academics.models


class Migration(migrations.Migration):
    dependencies = [("academics", "0007_academic_periods")]

    operations = [
        migrations.AlterField(
            model_name="classroom",
            name="academic_period",
            field=models.ForeignKey(
                default=academics.models.get_default_academic_period_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="classrooms",
                to="academics.academicperiod",
            ),
        ),
        migrations.AlterField(
            model_name="enrollment",
            name="academic_period",
            field=models.ForeignKey(
                default=academics.models.get_default_academic_period_id,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="enrollments",
                to="academics.academicperiod",
            ),
        ),
    ]
