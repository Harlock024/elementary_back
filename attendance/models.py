from django.db import models
from students.models import Student
import uuid

# Create your models here.
class CatalogTypeAtendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_type_attendances"

    def __str__(self):
        return self.name



class Attendance(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE, 
        related_name='attendances'
    )
    state_code = models.ForeignKey(
        CatalogTypeAtendance,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendances"
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"
