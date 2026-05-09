from grades.application.dto.grading_criteria_dto import CreateGradingCriteriaCommand, UpdateGradingCriteriaCommand
from grades.domain.exceptions.grading_criteria_exceptions import GradingCriteriaNotFoundError
from grades.models import GradingCriteria
from grades.serializer import GradingCriteriaSerializer


class DjangoGradingCriteriaRepository:
    def list_grading_criteria(self, class_room_id: str | None = None) -> list[dict]:
        qs = GradingCriteria.objects.all()
        if class_room_id:
            qs = qs.filter(class_room_id=class_room_id)
        return GradingCriteriaSerializer(qs, many=True).data

    def get_grading_criteria(self, grading_criteria_id: str) -> dict | None:
        gc = GradingCriteria.objects.filter(pk=grading_criteria_id).first()
        if gc is None:
            return None
        return GradingCriteriaSerializer(gc).data

    def create_grading_criteria(self, command: CreateGradingCriteriaCommand) -> dict:
        gc = GradingCriteria(
            name=command.name,
            class_room_id=command.class_room_id,
            percentage=command.percentage,
            is_attendance_based=command.is_attendance_based,
        )
        gc.save()
        return GradingCriteriaSerializer(gc).data

    def update_grading_criteria(self, command: UpdateGradingCriteriaCommand) -> dict:
        gc = GradingCriteria.objects.filter(pk=command.grading_criteria_id).first()
        if gc is None:
            raise GradingCriteriaNotFoundError("Grading Criteria not found")
        if command.name is not None:
            gc.name = command.name
        if command.class_room_id is not None:
            gc.class_room_id = command.class_room_id
        if command.percentage is not None:
            gc.percentage = command.percentage
        if command.is_attendance_based is not None:
            gc.is_attendance_based = command.is_attendance_based
        gc.save()
        return GradingCriteriaSerializer(gc).data

    def delete_grading_criteria(self, grading_criteria_id: str) -> None:
        gc = GradingCriteria.objects.filter(pk=grading_criteria_id).first()
        if gc is None:
            raise GradingCriteriaNotFoundError("Grading Criteria not found")
        gc.delete()
