from django.db import transaction

from academics.models import Enrollment, Group
from students.application.dto.student_dto import CreateStudentCommand
from students.domain.exceptions.student_exceptions import GroupNotFoundError
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
                first_name=command.first_name,
                second_name=command.second_name,
                last_name=command.last_name,
                date_of_birth=command.date_of_birth,
                gender=command.gender,
                state=command.state,
            )
            student.enrollment_number = Student.generate_enrollment_number()
            student.save()

            enrollment = Enrollment(
                student=student,
                group=group,
                period=command.period,
                state="active",
            )
            enrollment.save()

        return StudentSerializer(student).data
