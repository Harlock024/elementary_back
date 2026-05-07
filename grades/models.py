from django.db import models

from students.models import Student
from academics.models import ClassRoom, Subject
import uuid

# Create your models here.

class GradingCriteria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='grading_criteria'
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='grading_criteria'
    )
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "grading_criteria"

    def __str__(self):
        return f"{self.class_room} - {self.subject} - {self.type_code.code}"

# Calificaciones de los estudiantes
class StudentGrade(models.Model):
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
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='grades',
        default=1
    )
    assignment = models.ForeignKey(
        'assignments.Assignment',
        on_delete=models.CASCADE,
        related_name='grades',
        default=1
    )
    score = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_grades"

    def __str__(self):
        return f"{self.student} - {self.grading_criteria.name} ({self.score})"
