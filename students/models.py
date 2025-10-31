from django.db import models
from django.db.models import Max
from academics.models import Group
import uuid

class Student(models.Model):
    id =  models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30)
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
        from datetime import datetime
        prefix = f"E{datetime.now().year}"

        last_code = cls.objects.filter(enrollment_number__startswith=prefix).aggregate(max_code=Max('enrollment_number'))['max_code']
            
        last_number = 0
        if last_code:
            last_number = int(last_code.replace(prefix,""))

        return f"{prefix}{last_number + 1:05d}"
