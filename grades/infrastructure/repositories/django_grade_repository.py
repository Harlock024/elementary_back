from django.utils import timezone

from academics.models import ClassRoom, Subject
from grades.application.dto.grade_dto import CreateGradeCommand, UpdateGradeCommand
from grades.domain.exceptions.grade_exceptions import (
    CatalogTypeNotFoundError,
    ClassRoomNotFoundForGradeError,
    GradeNotFoundError,
    GradeVersionConflictError,
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
            id=command.id if command.id else None,
            student=student,
            subject=subject,
            class_room=class_room,
            score=command.score,
            max_score=command.max_score,
            description=command.description,
            type_code=catalog_type,
            syncStatus='pending',
            version=1,
            localUpdatedAt=timezone.now(),
        )
        student_grade.save()
        return StudentGradeSerializer(student_grade).data

    def update_grade(self, command: UpdateGradeCommand) -> dict:
        grade = StudentGrade.objects.filter(pk=command.grade_id).first()
        if grade is None:
            raise GradeNotFoundError("Grade not found")

        if command.version != grade.version:
            raise GradeVersionConflictError("Version conflict")

        if command.score is not None:
            grade.score = command.score
        if command.max_score is not None:
            grade.max_score = command.max_score
        if command.description is not None:
            grade.description = command.description
        if command.type_code_id is not None:
            catalog_type = CatalogTypeGrade.objects.filter(pk=command.type_code_id).first()
            if catalog_type:
                grade.type_code = catalog_type

        grade.version += 1
        grade.syncStatus = 'synced'
        grade.localUpdatedAt = timezone.now()

        grade.save()
        return StudentGradeSerializer(grade).data

    def delete_grade(self, grade_id: int) -> None:
        grade = StudentGrade.objects.filter(pk=grade_id).first()
        if grade is None:
            raise GradeNotFoundError("Grade not found")
        grade.delete()
