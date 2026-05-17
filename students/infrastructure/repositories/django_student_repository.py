from django.db import transaction

from academics.models import Enrollment, Group
from students.application.dto.student_dto import CreateStudentCommand, UpdateStudentCommand
from students.domain.exceptions.student_exceptions import GroupNotFoundError, StudentNotFoundError
from students.models import Student
from students.serializer import StudentDetailSerializer, StudentSerializer


class DjangoStudentRepository:
    def list_students_detail(self) -> list[dict]:
        students = Student.objects.all()
        return StudentDetailSerializer(students, many=True).data

    def list_students_by_group(self, group_id: str) -> list[dict]:
        students = Student.objects.filter(enrollment__group__id=group_id)
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
                curp=command.curp,
                tutor_name=command.tutor_name,
                tutor_phone=command.tutor_phone,
                tutor_relationship=command.tutor_relationship,
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

    def update_student(self, command: UpdateStudentCommand) -> dict:
        student = Student.objects.filter(pk=command.student_id).first()
        if student is None:
            raise StudentNotFoundError("Student not found")

        if command.first_name is not None:
            student.first_name = command.first_name
        if command.second_name is not None:
            student.second_name = command.second_name
        if command.last_name is not None:
            student.last_name = command.last_name
        if command.curp is not None:
            student.curp = command.curp
        if command.tutor_name is not None:
            student.tutor_name = command.tutor_name
        if command.tutor_phone is not None:
            student.tutor_phone = command.tutor_phone
        if command.tutor_relationship is not None:
            student.tutor_relationship = command.tutor_relationship
        if command.date_of_birth is not None:
            student.date_of_birth = command.date_of_birth
        if command.gender is not None:
            student.gender = command.gender
        if command.state is not None:
            student.state = command.state

        student.save()
        return StudentSerializer(student).data

    def delete_student(self, student_id: str) -> None:
        student = Student.objects.filter(pk=student_id).first()
        if student is None:
            raise StudentNotFoundError("Student not found")
        student.delete()
