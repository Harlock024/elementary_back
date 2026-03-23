from enum import unique
from django.db import models
from django.utils import timezone
from django.utils import tree
from academics.models import ClassRoom
from students.models import Student
import uuid


class SyncStatus(models.TextChoices):
    SYNCED = 'synced', 'Synced'
    PENDING = 'pending', 'Pending'
    CONFLICT = 'conflict', 'Conflict'

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE, 
        related_name='attendances'
    )
    state_code = models.ForeignKey(
        CatalogTypeAtendance,
        on_delete=models.RESTRICT,
        related_name='attendances'
    )

    class_room = models.ForeignKey(
        ClassRoom,
        on_delete=models.CASCADE,
        related_name='attendances',
        default=1
    )
    date = models.DateField()
    syncStatus = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.SYNCED)
    version = models.IntegerField(default=1)
    localUpdatedAt = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "attendances"
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"
