from django.db import models
from django.utils import timezone

from students.models import Student
from academics.models import ClassRoom, Subject
import uuid

# Create your models here.

class CatalogTypeGrade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "catalog_type_grades"

    def __str__(self):
        return self.code

# Calificaciones de los estudiantes
class StudentGrade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE, 
        related_name='grades'
    )
    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    type_code = models.ForeignKey(
        CatalogTypeGrade,
        on_delete=models.CASCADE,
        related_name='grades'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='grades',
        default=1
    )
    score = models.DecimalField(max_digits=5, decimal_places=2)
    max_score = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    syncStatus = models.CharField(
        max_length=20,
        choices=(
            ('synced', 'Synced'),
            ('pending', 'Pending'),
            ('conflict', 'Conflict'),
        ),
        default='synced',
    )
    version = models.IntegerField(default=1)
    localUpdatedAt = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_grades"

    def __str__(self):
        return f"{self.student} - {self.description or self.type_code.code} ({self.score}/{self.max_score})"
