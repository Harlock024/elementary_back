from academics.models import ClassRoom, Subject
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
    def list_grades(self, class_room_id: str | None = None) -> list[dict]:
        qs = StudentGrade.objects.select_related('student', 'subject', 'class_room', 'assignment')
        if class_room_id:
            qs = qs.filter(class_room_id=class_room_id)
        return StudentGradeSerializer(qs, many=True).data

    def get_grade(self, grade_id: int) -> dict | None:
        grade = StudentGrade.objects.filter(pk=grade_id).first()
        if grade is None:
            return None
        return StudentGradeSerializer(grade).data

    def create_grade(self, command: CreateGradeCommand) -> dict:
        student = Student.objects.filter(pk=command.student_id).first()
        if student is None:
            raise StudentNotFoundForGradeError("Student not found")

        class_room = ClassRoom.objects.filter(pk=command.class_room_id).first()
        if class_room is None:
            raise ClassRoomNotFoundForGradeError("ClassRoom not found")

        assignment = Assignment.objects.filter(pk=command.assignment_id).first()
        if assignment is None:
            raise AssignmentNotFoundForGradeError("Assignment not found")

        subject = Subject.objects.filter(pk=command.subject_id).first()
        if subject is None:
            raise SubjectNotFoundForGradeError("Subject not found")

        student_grade = StudentGrade(
            student=student,
            subject=subject,
            class_room=class_room,
            assignment=assignment,
            score=command.score,
            description=command.description,
            date=command.date,
        )
        student_grade.save()
        return StudentGradeSerializer(student_grade).data

    def update_grade(self, command: UpdateGradeCommand) -> dict:
        grade = StudentGrade.objects.filter(pk=command.grade_id).first()
        if grade is None:
            raise GradeNotFoundError("Grade not found")

        if command.score is not None:
            grade.score = command.score
        if command.description is not None:
            grade.description = command.description

        grade.save()
        return StudentGradeSerializer(grade).data

    def delete_grade(self, grade_id: int) -> None:
        grade = StudentGrade.objects.filter(pk=grade_id).first()
        if grade is None:
            raise GradeNotFoundError("Grade not found")
        grade.delete()
