from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser


class Staff(AbstractUser):

    ROLE_CHOICES = [
            ('Admin','Admin'),
            ('Principal','Principal'),
            ('Teacher','Teacher'),
        ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(max_length=150, blank=True)
    role = models.CharField(max_length=50,choices=ROLE_CHOICES,default='Teacher')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "staff"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    def is_admin(self):
        return self.role == 'Admin'
    def is_teacher(self):
        return self.role == 'Teacher'




