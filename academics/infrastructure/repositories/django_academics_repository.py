from django.db import transaction

from academics.application.dto.academics_dto import (
    UpdateClassRoomCommand,
    UpdateEnrollmentCommand,
    UpdateGroupCommand,
    UpdateSubjectCommand,
)
from academics.domain.exceptions.academics_exceptions import (
    ClassRoomHistoryConflictError,
    ClassRoomNotFoundError,
    EnrollmentNotFoundError,
    GroupNotFoundError,
    SubjectNotFoundError,
)
from academics.models import ClassRoom, Enrollment, Group, Subject
from academics.serializer import (
    ClassRoomSerializer,
    EnrollmentSerializer,
    GroupSerializer,
    SubjectSerializer,
)


class DjangoGroupRepository:
    def list_groups(self) -> list[dict]:
        groups = Group.objects.all()
        return GroupSerializer(groups, many=True).data

    def get_group(self, group_id: str) -> dict | None:
        group = Group.objects.filter(pk=group_id).first()
        if group is None:
            return None
        return GroupSerializer(group).data

    def update_group(self, command: UpdateGroupCommand) -> dict:
        group = Group.objects.filter(pk=command.group_id).first()
        if group is None:
            raise GroupNotFoundError("Group not found")

        if command.letter is not None:
            group.letter = command.letter
        if command.school_grade_id is not None:
            from academics.models import SchoolGrade
            school_grade = SchoolGrade.objects.filter(pk=command.school_grade_id).first()
            if school_grade:
                group.school_grade = school_grade

        group.save()
        return GroupSerializer(group).data
    
    def delete_group(self, group_id: str) -> None:
        group = Group.objects.filter(pk=group_id).first()
        if group is None:
            raise GroupNotFoundError("Group not found")
        group.delete()


class DjangoSubjectRepository:
    def list_subjects(self) -> list[dict]:
        subjects = Subject.objects.all()
        return SubjectSerializer(subjects, many=True).data

    def get_subject(self, subject_id: str) -> dict | None:
        subject = Subject.objects.filter(pk=subject_id).first()
        if subject is None:
            return None
        return SubjectSerializer(subject).data

    def update_subject(self, command: UpdateSubjectCommand) -> dict:
        subject = Subject.objects.filter(pk=command.subject_id).first()
        if subject is None:
            raise SubjectNotFoundError("Subject not found")

        if command.name is not None:
            subject.name = command.name
        if command.description is not None:
            subject.description = command.description
        if command.school_grade_id is not None:
            from academics.models import SchoolGrade
            school_grade = SchoolGrade.objects.filter(pk=command.school_grade_id).first()
            if school_grade:
                subject.school_grade = school_grade

        subject.save()
        return SubjectSerializer(subject).data

    def delete_subject(self, subject_id: str) -> None:
        subject = Subject.objects.filter(pk=subject_id).first()
        if subject is None:
            raise SubjectNotFoundError("Subject not found")
        subject.delete()

class DjangoClassRoomRepository:
    def list_classrooms(self) -> list[dict]:
        classrooms = ClassRoom.objects.all()
        return ClassRoomSerializer(classrooms, many=True).data

    def get_classroom(self, classroom_id: str) -> dict | None:
        classroom = ClassRoom.objects.filter(pk=classroom_id).first()
        if classroom is None:
            return None
        return ClassRoomSerializer(classroom).data

    @transaction.atomic
    def update_classroom(self, command: UpdateClassRoomCommand) -> dict:
        classroom = (
            ClassRoom.objects.select_for_update()
            .filter(pk=command.classroom_id)
            .first()
        )
        if classroom is None:
            raise ClassRoomNotFoundError("ClassRoom not found")

        changes_group = (
            command.group_id is not None
            and str(command.group_id) != str(classroom.group_id)
        )
        changes_staff = (
            command.staff_id is not None
            and str(command.staff_id) != str(classroom.staff_id)
        )
        has_history = any(
            (
                classroom.attendances.exists(),
                classroom.assignments.exists(),
                classroom.grades.exists(),
                classroom.grading_criteria.exists(),
            )
        )
        if (changes_group or changes_staff) and has_history:
            raise ClassRoomHistoryConflictError(
                "No se puede reasignar un aula que contiene historial académico."
            )

        if command.group_id is not None:
            group = Group.objects.filter(pk=command.group_id).first()
            if group:
                classroom.group = group
        if command.staff_id is not None:
            from staff.models import Staff
            staff = Staff.objects.filter(pk=command.staff_id).first()
            if staff:
                classroom.staff = staff

        classroom.save()
        return ClassRoomSerializer(classroom).data

    def delete_classroom(self, classroom_id: str) -> None:
        classroom = ClassRoom.objects.filter(pk=classroom_id).first()
        if classroom is None:
            raise ClassRoomNotFoundError("ClassRoom not found")
        classroom.delete()


class DjangoEnrollmentRepository:
    def list_enrollments(self) -> list[dict]:
        enrollments = Enrollment.objects.all()
        return EnrollmentSerializer(enrollments, many=True).data

    def list_enrollments_by_state(self, state: str) -> list[dict]:
        enrollments = Enrollment.objects.filter(state=state)
        return EnrollmentSerializer(enrollments, many=True).data

    def list_enrollments_by_student(self, student_id: str) -> list[dict]:
        enrollments = Enrollment.objects.filter(student_id=student_id)
        return EnrollmentSerializer(enrollments, many=True).data

    def get_enrollment(self, enrollment_id: str) -> dict | None:
        enrollment = Enrollment.objects.filter(pk=enrollment_id).first()
        if enrollment is None:
            return None
        return EnrollmentSerializer(enrollment).data

    def update_enrollment(self, command: UpdateEnrollmentCommand) -> dict:
        from django.db import transaction
        from academics.models import AcademicPeriod

        with transaction.atomic():
            enrollment = Enrollment.objects.select_for_update().select_related(
                "academic_period"
            ).filter(pk=command.enrollment_id).first()
            if enrollment is None:
                raise EnrollmentNotFoundError("Enrollment not found")
            if enrollment.academic_period.status == AcademicPeriod.Status.CLOSED:
                raise ValueError("The academic period is closed")
            if command.student_id is not None:
                from students.models import Student
                student = Student.objects.filter(pk=command.student_id).first()
                if student:
                    enrollment.student = student
            if command.group_id is not None:
                group = Group.objects.filter(pk=command.group_id).first()
                if group:
                    enrollment.group = group
            if command.academic_period_id is not None or command.period is not None:
                lookup = (
                    {"pk": command.academic_period_id}
                    if command.academic_period_id is not None
                    else {"name": command.period}
                )
                target_period = AcademicPeriod.objects.select_for_update().filter(**lookup).first()
                if target_period is None or target_period.status == AcademicPeriod.Status.CLOSED:
                    raise ValueError("Academic period not found or closed")
                enrollment.academic_period = target_period
                enrollment.period = target_period.name
            if command.state is not None:
                enrollment.state = command.state

            enrollment.save()
        return EnrollmentSerializer(enrollment).data
    
    def delete_enrollment(self, enrollment_id: str) -> None:
        enrollment = Enrollment.objects.select_related("academic_period").filter(pk=enrollment_id).first()
        if enrollment is None:
            raise EnrollmentNotFoundError("Enrollment not found")
        if enrollment.academic_period.status == "closed":
            raise ValueError("The academic period is closed")
        enrollment.state = 'inactivo'
        enrollment.save(update_fields=['state', 'updated_at'])
