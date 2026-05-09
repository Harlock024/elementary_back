from datetime import datetime
from django.db import models, transaction
from django.db.models import Max
import uuid


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30)
    curp = models.CharField(max_length=18, unique=True)
    tutor_name = models.CharField(max_length=30)
    tutor_phone = models.CharField(max_length=30)
    tutor_relationship = models.CharField(max_length=30)
    enrollment_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    state = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "students"
        indexes = [
            models.Index(fields=['enrollment_number'], name='idx_enrollment_number'),
        ]

    @classmethod
    def generate_enrollment_number(cls):
        with transaction.atomic():
            year = datetime.now().year
            prefix = f"E{year}"
            last_code_date = cls.objects.filter(
                enrollment_number__startswith=prefix
            ).select_for_update().aggregate(Max('enrollment_number'))
            last_code = last_code_date['enrollment_number__max']
            last_number = 0
            if last_code:
                last_number_str = last_code.replace(prefix, "")
                if last_number_str.isdigit():
                    last_number = int(last_number_str)
            new_number = last_number + 1
            return f"{prefix}{str(new_number).zfill(4)}"
