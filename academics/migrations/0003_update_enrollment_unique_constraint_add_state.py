from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0002_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
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
    ]
