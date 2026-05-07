from grades.application.dto.grading_criteria_dto import CreateGradingCriteriaCommand , UpdateGradingCriteriaCommand
from grades.domain.exceptions.grade_exceptions import (
    CatalogTypeNotFoundError,
    ClassRoomNotFoundForGradeError, 
    GradeNotFoundError,
    StudentNotFoundForGradeError,
    SubjectNotFoundForGradeError,
)

from grades.domain.exceptions.grading_criteria_exceptions import GradingCriteriaNotFoundError
from grades.models import StudentGrade,GradingCriteria

from grades.serializer import StudentGradeSerializer, GradingCriteriaSerializer


class DjangoGradingCriteriaRepository:
    def list_grading_criteria(self, class_room_id: str | None = None) -> list[dict]:
        queryset = GradingCriteria.objects.all()
        if class_room_id:
            queryset = queryset.filter(class_room__id=class_room_id)
        return GradingCriteriaSerializer(queryset, many=True).data

    def get_grading_criteria(self, grading_criteria_id: str) -> dict | None:
        grading_criteria = GradingCriteria.objects.filter(pk=grading_criteria_id).first()
        if grading_criteria is None:
            return None
        return GradingCriteriaSerializer(grading_criteria).data

    def create_grading_criteria(self, command: CreateGradingCriteriaCommand) -> dict:
        grading_criteria = GradingCriteria(
            name=command.name,
            class_room_id=command.class_room_id,
            subject_id=command.subject_id,
            percentage=command.percentage,
        )
        grading_criteria.save()
        return GradingCriteriaSerializer(grading_criteria).data

    def update_grading_criteria(self, command: UpdateGradingCriteriaCommand) -> dict:
        grading_criteria = GradingCriteria.objects.filter(pk=command.id).first()
        if grading_criteria is None:
            raise GradingCriteriaNotFoundError("Grading Criteria not found")
        grading_criteria.name = command.name
        grading_criteria.class_room_id = command.class_room_id
        grading_criteria.subject_id = command.subject_id
        grading_criteria.percentage = command.percentage
        grading_criteria.save()
        return GradingCriteriaSerializer(grading_criteria).data

    def delete_grading_criteria(self, grading_criteria_id: str) -> None:
        grading_criteria = GradingCriteria.objects.filter(pk=grading_criteria_id).first()
        if grading_criteria is None:
            raise GradingCriteriaNotFoundError("Grading Criteria not found")
        grading_criteria.delete()