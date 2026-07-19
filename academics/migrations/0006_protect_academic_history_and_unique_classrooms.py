import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("academics", "0005_alter_schoolgrade_name_alter_subject_description_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="enrollment",
            name="student",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="enrollments",
                to="students.student",
            ),
        ),
        migrations.AlterField(
            model_name="enrollment",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="enrollments",
                to="academics.group",
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="school_grade",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="groups",
                to="academics.schoolgrade",
            ),
        ),
        migrations.AlterField(
            model_name="subject",
            name="school_grade",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subjects",
                to="academics.schoolgrade",
            ),
        ),
        migrations.AlterField(
            model_name="classroom",
            name="staff",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="classes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="classroom",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="classes",
                to="academics.group",
            ),
        ),
        migrations.AddConstraint(
            model_name="group",
            constraint=models.UniqueConstraint(
                fields=("school_grade", "letter"),
                name="uniq_group_school_grade_letter",
            ),
        ),
        migrations.AddConstraint(
            model_name="classroom",
            constraint=models.UniqueConstraint(
                fields=("group",),
                name="uniq_classroom_group",
            ),
        ),
        migrations.AddIndex(
            model_name="classroom",
            index=models.Index(
                fields=["staff", "group"],
                name="idx_staff_group",
            ),
        ),
    ]
