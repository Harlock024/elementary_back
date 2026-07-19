from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("staff", "0003_alter_staff_email_alter_staff_first_name_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="staff",
            name="password_professor",
        ),
        migrations.AlterField(
            model_name="staff",
            name="role",
            field=models.CharField(
                choices=[
                    ("Admin", "Admin"),
                    ("Principal", "Principal"),
                    ("Teacher", "Teacher"),
                ],
                default="Teacher",
                max_length=50,
            ),
        ),
    ]
