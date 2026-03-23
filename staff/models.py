from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.models import AbstractUser


class SyncStatus(models.TextChoices):
    SYNCED = 'synced', 'Synced'
    PENDING = 'pending', 'Pending'
    CONFLICT = 'conflict', 'Conflict'


class Staff(AbstractUser):

    ROLE_CHOICES = [
            ('admin','Admin'),
            ('teacher','Teacher'),
        ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='teacher')
    password_professor = models.CharField(max_length=128, blank=True, null=True)
    syncStatus = models.CharField(max_length=20, choices=SyncStatus.choices, default=SyncStatus.SYNCED)
    version = models.IntegerField(default=1)
    localUpdatedAt = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "staff"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    def is_admin(self):
        return self.role == 'admin'
    def is_teacher(self):
        return self.role == 'teacher'






