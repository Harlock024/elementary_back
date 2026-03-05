from academics.models import ClassRoom, Subject
from grades.application.dto.grade_dto import CreateGradeCommand
from grades.domain.exceptions.grade_exceptions import (
    CatalogTypeNotFoundError,
    ClassRoomNotFoundForGradeError,
    StudentNotFoundForGradeError,
    SubjectNotFoundForGradeError,
)
from grades.models import CatalogTypeGrade, StudentGrade
from grades.serializer import StudentGradeSerializer
from students.models import Student


class DjangoGradeRepository:
    def list_grades(self, class_room_id: str | None = None) -> list[dict]:
        queryset = StudentGrade.objects.all()
        if class_room_id:
            queryset = queryset.filter(class_room__id=class_room_id)
        return StudentGradeSerializer(queryset, many=True).data

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

        catalog_type = CatalogTypeGrade.objects.filter(pk=command.type_code_id).first()
        if catalog_type is None:
            raise CatalogTypeNotFoundError("Catalog Type not found")

        subject = Subject.objects.filter(pk=command.subject_id).first()
        if subject is None:
            raise SubjectNotFoundForGradeError(
                "Subject not found in the specified ClassRoom"
            )

        student_grade = StudentGrade(
            student=student,
            subject=subject,
            class_room=class_room,
            score=command.score,
            max_score=command.max_score,
            description=command.description,
            type_code=catalog_type,
        )
        student_grade.save()
        return StudentGradeSerializer(student_grade).data
