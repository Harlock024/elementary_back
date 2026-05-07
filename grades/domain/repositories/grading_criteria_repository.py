from typing import Protocol


from grades.application.dto.grading_criteria_dto import CreateGradingCriteriaCommand, UpdateGradingCriteriaCommand


class GradingCriteriaRepository(Protocol):
    def list_grading_criteria(self, class_room_id: str | None = None) -> list[dict]:
        ...

    def get_grading_criteria(self, grading_criteria_id: str) -> dict | None:
        ...

    def create_grading_criteria(self, command: CreateGradingCriteriaCommand) -> dict:
        ...

    def update_grading_criteria(self, command: UpdateGradingCriteriaCommand) -> dict:
        ...

    def delete_grading_criteria(self, grading_criteria_id: str) -> None:
        ...