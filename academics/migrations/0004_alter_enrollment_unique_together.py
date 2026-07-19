from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0003_update_enrollment_unique_constraint_add_state'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='enrollment',
            unique_together={('student', 'period', 'group')},
        ),
    ]
