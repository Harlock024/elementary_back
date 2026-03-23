from django.db import models
from django.utils import timezone
import uuid
import staff


class Enrollment(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        student = models.ForeignKey(
                'students.Student',
                on_delete=models.CASCADE,
                related_name='enrollments'
        )
        group = models.ForeignKey(
                'academics.Group',
                on_delete=models.CASCADE,
                related_name='enrollments'
        )
        period = models.CharField(max_length=20)
        enrollment_date = models.DateField(auto_now_add=True)
        state = models.CharField(max_length=20, default='active')
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
                db_table = "enrollments"
                unique_together = ('student', 'period', 'group')


class SchoolGrade(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        name = models.CharField(max_length=5)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
                db_table = "school_grades"


class Group(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        letter = models.CharField(max_length=5)
        school_grade = models.ForeignKey(
                SchoolGrade,
                on_delete=models.CASCADE,
                related_name='groups'
        )
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
                db_table = "groups"


class Subject(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        name = models.CharField(max_length=50)
        school_grade = models.ForeignKey(
                SchoolGrade,
                on_delete=models.CASCADE,
                related_name='subjects'
        )
        description = models.TextField(blank=True, null=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
                db_table = "subjects"


class ClassRoom(models.Model):
        id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
        staff = models.ForeignKey(
                staff.models.Staff,
                on_delete=models.CASCADE,
                related_name='classes'
        )
        group = models.ForeignKey(
                Group,
                on_delete=models.CASCADE,
                related_name='classes'
        )

        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
                db_table = "class_rooms"

        indexes = [
                models.Index(fields=['staff', 'group'], name='idx_staff_group'),
        ]


