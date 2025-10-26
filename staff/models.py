from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser


class Staff(AbstractUser):

    ROLE_CHOICES = [
            ('directora','directora'),
            ('admin','admin'),
            ('profesor','profesor'),
        ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='profesor')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        db_table = "staff"

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def is_directora(self):
        return self.role == 'directora'

    def is_admin(self):
        return self.role == 'admin'

    def is_profesor(self):
        return self.role == 'profesor'






