from django.db import transaction
from django.utils import timezone

from academics.models import Enrollment, Group
from students.application.dto.student_dto import CreateStudentCommand, UpdateStudentCommand
from students.domain.exceptions.student_exceptions import (
    GroupNotFoundError,
    StudentNotFoundError,
    StudentVersionConflictError,
)
from students.models import Student
from students.serializer import StudentDetailSerializer, StudentSerializer


class DjangoStudentRepository:
    def list_students_detail(self) -> list[dict]:
        students = Student.objects.all()
        return StudentDetailSerializer(students, many=True).data

    def get_student_detail(self, student_id: str) -> dict | None:
        student = Student.objects.filter(pk=student_id).first()
        if student is None:
            return None
        return StudentDetailSerializer(student).data

    def create_student_with_enrollment(self, command: CreateStudentCommand) -> dict:
        group = Group.objects.filter(pk=command.group_id).first()
        if group is None:
            raise GroupNotFoundError("Group not found")

        with transaction.atomic():
            student = Student(
                id=command.id if command.id else None,
                first_name=command.first_name,
                second_name=command.second_name,
                last_name=command.last_name,
                date_of_birth=command.date_of_birth,
                gender=command.gender,
                state=command.state,
                syncStatus='pending',
                version=1,
                localUpdatedAt=timezone.now(),
            )
            student.enrollment_number = Student.generate_enrollment_number()
            student.save()

            enrollment = Enrollment(
                student=student,
                group=group,
                period=command.period,
                state="active",
                syncStatus='pending',
                version=1,
                localUpdatedAt=timezone.now(),
            )
            enrollment.save()

        return StudentSerializer(student).data

    def update_student(self, command: UpdateStudentCommand) -> dict:
        student = Student.objects.filter(pk=command.student_id).first()
        if student is None:
            raise StudentNotFoundError("Student not found")

        if command.version != student.version:
            raise StudentVersionConflictError("Version conflict")

        if command.first_name is not None:
            student.first_name = command.first_name
        if command.second_name is not None:
            student.second_name = command.second_name
        if command.last_name is not None:
            student.last_name = command.last_name
        if command.date_of_birth is not None:
            student.date_of_birth = command.date_of_birth
        if command.gender is not None:
            student.gender = command.gender
        if command.state is not None:
            student.state = command.state

        student.version += 1
        student.syncStatus = 'synced'
        student.localUpdatedAt = timezone.now()

        student.save()
        return StudentSerializer(student).data

    def delete_student(self, student_id: str) -> None:
        student = Student.objects.filter(pk=student_id).first()
        if student is None:
            raise StudentNotFoundError("Student not found")
        student.delete()
