from django.db import models
from django.db.models import Q
import uuid
import staff 


class AcademicPeriod(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        ACTIVE = "active", "Activo"
        CLOSED = "closed", "Cerrado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "academic_periods"
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                condition=Q(start_date__lt=models.F("end_date")),
                name="academic_period_dates_ordered",
            ),
            models.UniqueConstraint(
                fields=["status"],
                condition=Q(status="active"),
                name="uniq_active_academic_period",
            ),
        ]

    def __str__(self):
        return self.name


def get_default_academic_period_id():
    period = AcademicPeriod.objects.filter(status=AcademicPeriod.Status.ACTIVE).first()
    if period is None:
        period = AcademicPeriod.objects.order_by("-start_date").first()
    if period is None:
        from datetime import date

        today = date.today()
        year = today.year if today.month >= 8 else today.year - 1
        period = AcademicPeriod.objects.create(
            name=f"{year}-{year + 1}",
            start_date=date(year, 8, 1),
            end_date=date(year + 1, 7, 31),
            status=AcademicPeriod.Status.ACTIVE,
        )
    return period.pk


class Enrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
            'students.Student', 
            on_delete=models.PROTECT,
            related_name='enrollments'
    )
    group = models.ForeignKey(
            'academics.Group', 
            on_delete=models.PROTECT,
            related_name='enrollments'
    )
    period = models.CharField(max_length=20)
    academic_period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.PROTECT,
        related_name="enrollments",
        default=get_default_academic_period_id,
    )
    enrollment_date = models.DateField(auto_now_add=True)
    state = models.CharField(max_length=20, default='activo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "enrollments"
        constraints = [
            models.UniqueConstraint(
                fields=["student", "academic_period", "group"],
                name="uniq_student_period_group",
            ),
        ]


# Nivel Escolar ej 1ro, 2do, 3ro, 4to, 5to, 6to
class SchoolGrade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "school_grades"

# Grupo dentro del nivel escolar ej A, B, C
class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    letter = models.CharField(max_length=5)
    school_grade = models.ForeignKey(
            SchoolGrade, 
            on_delete=models.PROTECT,
            related_name='groups'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = "groups"
        constraints = [
            models.UniqueConstraint(
                fields=['school_grade', 'letter'],
                name='uniq_group_school_grade_letter',
            ),
        ]


class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    school_grade = models.ForeignKey(
            SchoolGrade, 
            on_delete=models.PROTECT,
            related_name='subjects'
    )
    description = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subjects"

class ClassRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    staff = models.ForeignKey(
            staff.models.Staff,
            on_delete=models.PROTECT,
            related_name='classes'
    )
    group = models.ForeignKey(
            Group,
            on_delete=models.PROTECT,
            related_name='classes'
            )
    academic_period = models.ForeignKey(
        AcademicPeriod,
        on_delete=models.PROTECT,
        related_name="classrooms",
        default=get_default_academic_period_id,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "class_rooms"
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'academic_period'],
                name='uniq_classroom_group_period',
            ),
        ]
        indexes = [
            models.Index(fields=['staff', 'group'], name='idx_staff_group'),
        ]
