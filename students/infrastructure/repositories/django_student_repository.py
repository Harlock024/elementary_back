from django.db import transaction
from django.db.models import Prefetch

from academics.models import Enrollment, Group
from grades.models import StudentGrade
from students.application.dto.student_dto import CreateStudentCommand, UpdateStudentCommand
from students.domain.exceptions.student_exceptions import GroupNotFoundError, StudentNotFoundError
from students.models import Student
from students.serializer import StudentDetailSerializer, StudentProfileSerializer, StudentSerializer


class DjangoStudentRepository:
    def list_students_detail(self) -> list[dict]:
        students = Student.objects.all()
        return StudentDetailSerializer(students, many=True).data

    def list_students_by_group(self, group_id: str) -> list[dict]:
        students = Student.objects.filter(
            enrollments__group__id=group_id,
            enrollments__state='activo',
        ).prefetch_related(
            Prefetch(
                'enrollments',
                queryset=Enrollment.objects.filter(group_id=group_id),
                to_attr='detail_enrollments',
            )
        )
        return StudentDetailSerializer(students, many=True).data

    def list_students_by_classroom(self, classroom_id: str) -> list[dict]:
        students = Student.objects.filter(
            enrollments__group__classes__id=classroom_id,
            enrollments__state='activo',
        ).prefetch_related(
            Prefetch(
                'enrollments',
                queryset=Enrollment.objects.filter(
                    group__classes__id=classroom_id,
                ).distinct(),
                to_attr='detail_enrollments',
            )
        ).distinct()
        return StudentDetailSerializer(students, many=True).data
    
    def get_student_detail(
        self,
        student_id: str,
        classroom_ids: list[str] | None = None,
    ) -> dict | None:
        students = Student.objects.filter(pk=student_id)
        if classroom_ids is not None:
            students = students.prefetch_related(
                Prefetch(
                    'enrollments',
                    queryset=Enrollment.objects.filter(
                        group__classes__id__in=classroom_ids,
                    ).distinct(),
                    to_attr='detail_enrollments',
                )
            )
        student = students.first()
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
                state=command.state,
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

        with transaction.atomic():
            student.save()

            if command.group_id is not None:
                group = Group.objects.filter(pk=command.group_id).first()
                if group is None:
                    raise GroupNotFoundError("Group not found")

                active_enrollment = Enrollment.objects.filter(
                    student=student, state='activo'
                ).select_related('group').first()

                period = command.period or (active_enrollment.period if active_enrollment else None)
                if period is None:
                    raise ValueError("period is required when changing group")

                if active_enrollment and str(active_enrollment.group_id) != str(group.id):
                    Enrollment.objects.filter(
                        student=student, state='activo'
                    ).update(state='inactivo')

                Enrollment.objects.get_or_create(
                    student=student,
                    group=group,
                    period=period,
                    defaults={'state': 'activo'},
                )

        return StudentSerializer(student).data

    def delete_student(self, student_id: str) -> None:
        student = Student.objects.filter(pk=student_id).first()
        if student is None:
            raise StudentNotFoundError("Student not found")
        student.delete()

    def get_student_profile(
        self,
        student_id: str,
        classroom_ids: list[str] | None = None,
    ) -> dict | None:
        enrollments = Enrollment.objects.select_related(
            'group__school_grade'
        ).order_by('-created_at')
        grades = StudentGrade.objects.select_related(
            'assignment__subject',
            'class_room',
        )

        if classroom_ids is not None:
            enrollments = enrollments.filter(
                group__classes__id__in=classroom_ids,
            ).distinct()
            grades = grades.filter(class_room_id__in=classroom_ids)

        student = (
            Student.objects
            .prefetch_related(
                Prefetch(
                    'enrollments',
                    queryset=enrollments,
                    to_attr='profile_enrollments',
                ),
                Prefetch(
                    'grades',
                    queryset=grades,
                    to_attr='profile_grades',
                ),
            )
            .filter(pk=student_id)
            .first()
        )
        if student is None:
            return None
        return StudentProfileSerializer(student).data
