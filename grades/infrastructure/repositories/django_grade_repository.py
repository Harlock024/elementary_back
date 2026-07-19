from django.db import IntegrityError, transaction

from academics.models import ClassRoom, Enrollment, Subject
from assignments.models import Assignment
from grades.application.dto.grade_dto import CreateGradeCommand, UpdateGradeCommand
from grades.domain.exceptions.grade_exceptions import (
    AssignmentNotFoundForGradeError,
    ClassRoomNotFoundForGradeError,
    GradeNotFoundError,
    StudentNotFoundForGradeError,
    SubjectNotFoundForGradeError,
)
from grades.models import StudentGrade
from grades.serializer import StudentGradeSerializer
from students.models import Student


class DjangoGradeRepository:
    def list_grades(self, class_room_id: str | None = None, student_id: str | None = None) -> list[dict]:
        qs = StudentGrade.objects.select_related('student', 'subject', 'class_room', 'assignment__subject')
        if class_room_id:
            qs = qs.filter(class_room_id=class_room_id)
        if student_id:
            qs = qs.filter(student_id=student_id)
        return StudentGradeSerializer(qs, many=True).data

    def get_grade(self, grade_id: int) -> dict | None:
        grade = StudentGrade.objects.filter(pk=grade_id).first()
        if grade is None:
            return None
        return StudentGradeSerializer(grade).data

    def create_grade(self, command: CreateGradeCommand) -> dict:
        with transaction.atomic():
            class_room = ClassRoom.objects.select_for_update().select_related(
                "academic_period"
            ).filter(pk=command.class_room_id).first()
            if class_room is None:
                raise ClassRoomNotFoundForGradeError("ClassRoom not found")
            if class_room.academic_period.status == "closed":
                raise ValueError("The academic period is closed")
            student = Student.objects.select_for_update().filter(pk=command.student_id).first()
            if student is None:
                raise StudentNotFoundForGradeError("Student not found")
            assignment = Assignment.objects.select_for_update().filter(pk=command.assignment_id).first()
            if assignment is None:
                raise AssignmentNotFoundForGradeError("Assignment not found")
            subject = Subject.objects.filter(pk=command.subject_id).first()
            if subject is None:
                raise SubjectNotFoundForGradeError("Subject not found")
            if assignment.class_room_id != class_room.id:
                raise ValueError("Assignment must belong to classroom")
            if assignment.subject_id != subject.id:
                raise ValueError("Subject must match assignment")
            if not Enrollment.objects.select_for_update().filter(
                student=student,
                group_id=class_room.group_id,
                academic_period_id=class_room.academic_period_id,
                state__in=("activo", "active"),
            ).exists():
                raise ValueError("Student is not enrolled in this classroom period")
            if command.score < 0 or command.score > assignment.max_score:
                raise ValueError("Score must be between zero and assignment max score")
            if not class_room.academic_period.start_date <= command.date <= class_room.academic_period.end_date:
                raise ValueError("Grade date is outside the academic period")
            try:
                student_grade = StudentGrade.objects.create(
                    student=student,
                    subject=subject,
                    class_room=class_room,
                    assignment=assignment,
                    score=command.score,
                    description=command.description,
                    date=command.date,
                )
            except IntegrityError as exc:
                raise ValueError("A grade already exists for this student and assignment") from exc
        return StudentGradeSerializer(student_grade).data

    def update_grade(self, command: UpdateGradeCommand) -> dict:
        grade = StudentGrade.objects.select_related("class_room__academic_period", "assignment").filter(pk=command.grade_id).first()
        if grade is None:
            raise GradeNotFoundError("Grade not found")
        if grade.class_room.academic_period.status == "closed":
            raise ValueError("The academic period is closed")

        if command.score is not None:
            if command.score < 0 or command.score > grade.assignment.max_score:
                raise ValueError("Score must be between zero and assignment max score")
            grade.score = command.score
        if command.description is not None:
            grade.description = command.description

        grade.save()
        return StudentGradeSerializer(grade).data

    def delete_grade(self, grade_id: int) -> None:
        grade = StudentGrade.objects.select_related("class_room__academic_period").filter(pk=grade_id).first()
        if grade is None:
            raise GradeNotFoundError("Grade not found")
        if grade.class_room.academic_period.status == "closed":
            raise ValueError("The academic period is closed")
        grade.delete()
