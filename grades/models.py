from django.db import models
import uuid

from academics.models import ClassRoom, Subject
from students.models import Student


class GradingCriteria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='grading_criteria'
    )
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_attendance_based = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "grading_criteria"
        indexes = [
            models.Index(fields=['class_room'], name='gc_class_room_idx'),
        ]

    def __str__(self):
        return self.name


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
        related_name='grades'
    )
    assignment = models.ForeignKey(
        'assignments.Assignment',
        on_delete=models.CASCADE,
        related_name='grades'
    )
    score = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_grades"
        indexes = [
            models.Index(fields=['assignment'], name='sg_assignment_idx'),
        ]

    def __str__(self):
        return f"{self.student} ({self.score})"
