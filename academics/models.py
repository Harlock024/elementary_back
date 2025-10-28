from django.db import models
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "enrollments"
        unique_together = ('student', 'period',"group")


# Nivel Escolar ej 1ro, 2do, 3ro, 4to, 5to, 6to
class SchoolGrade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=5)
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

