from django.db import transaction
from django.db.models import Sum

from academics.models import ClassRoom
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
        with transaction.atomic():
            classroom = ClassRoom.objects.select_for_update().select_related("academic_period").filter(pk=command.class_room_id).first()
            if classroom is None:
                raise ValueError("Classroom not found")
            if classroom.academic_period.status == "closed":
                raise ValueError("The academic period is closed")
            current = GradingCriteria.objects.select_for_update().filter(
                class_room=classroom
            ).aggregate(total=Sum("percentage"))["total"] or 0
            if command.percentage <= 0 or current + command.percentage > 100:
                raise ValueError("Criteria percentages must be positive and cannot exceed 100")
            gc = GradingCriteria.objects.create(
                name=command.name,
                class_room=classroom,
                percentage=command.percentage,
                is_attendance_based=command.is_attendance_based,
            )
        return GradingCriteriaSerializer(gc).data

    def update_grading_criteria(self, command: UpdateGradingCriteriaCommand) -> dict:
        with transaction.atomic():
            gc = GradingCriteria.objects.select_for_update().select_related("class_room__academic_period").filter(pk=command.grading_criteria_id).first()
            if gc is None:
                raise GradingCriteriaNotFoundError("Grading Criteria not found")
            if gc.class_room.academic_period.status == "closed":
                raise ValueError("The academic period is closed")
            target_id = command.class_room_id or gc.class_room_id
            target = ClassRoom.objects.select_for_update().select_related("academic_period").filter(pk=target_id).first()
            if target is None:
                raise ValueError("Classroom not found")
            if target.academic_period.status == "closed":
                raise ValueError("The academic period is closed")
            if command.class_room_id is not None and gc.assignments.exists() and target.id != gc.class_room_id:
                raise ValueError("Grading criteria in use cannot be moved")
            percentage = command.percentage if command.percentage is not None else gc.percentage
            current = GradingCriteria.objects.select_for_update().filter(
                class_room=target
            ).exclude(pk=gc.pk).aggregate(total=Sum("percentage"))["total"] or 0
            if percentage <= 0 or current + percentage > 100:
                raise ValueError("Criteria percentages must be positive and cannot exceed 100")
            if command.name is not None:
                gc.name = command.name
            gc.class_room = target
            gc.percentage = percentage
            if command.is_attendance_based is not None:
                gc.is_attendance_based = command.is_attendance_based
            gc.save()
        return GradingCriteriaSerializer(gc).data

    def delete_grading_criteria(self, grading_criteria_id: str) -> None:
        gc = GradingCriteria.objects.select_related("class_room__academic_period").filter(pk=grading_criteria_id).first()
        if gc is None:
            raise GradingCriteriaNotFoundError("Grading Criteria not found")
        if gc.class_room.academic_period.status == "closed":
            raise ValueError("The academic period is closed")
        gc.delete()
