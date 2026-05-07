from grades.application.dto.grading_criteria_dto import CreateGradingCriteriaCommand, UpdateGradingCriteriaCommand
from grades.domain.entities.grading_criteria_entity import GradingCriteriaEntity
from grades.domain.exceptions.grading_criteria_exceptions import GradingCriteriaNotFoundError
from grades.domain.repositories.grading_criteria_repository import GradingCriteriaRepository


class ListGradingCriteriaUseCase:
    def __init__(self, repository: GradingCriteriaRepository):
        self.repository = repository

    def execute(self, class_room_id: str | None = None) -> list[dict]:
        return self.repository.list_grading_criteria(class_room_id=class_room_id)
    

class GetGradingCriteriaUseCase:
    def __init__(self, repository: GradingCriteriaRepository):
        self.repository = repository

    def execute(self, grading_criteria_id: str) -> dict:
        grading_criteria = self.repository.get_grading_criteria(grading_criteria_id)
        if grading_criteria is None:
            raise GradingCriteriaNotFoundError("Grading Criteria not found")
        return grading_criteria
    

class CreateGradingCriteriaUseCase:
    def __init__(self, repository: GradingCriteriaRepository):
        self.repository = repository

    def execute(self, command: CreateGradingCriteriaCommand) -> dict:
        GradingCriteriaEntity(
            name=command.name,
            class_room_id=command.class_room_id,
            subject_id=command.subject_id,
            percentage=command.percentage,
        )
        return self.repository.create_grading_criteria(command)
    

class UpdateGradingCriteriaUseCase:
    def __init__(self, repository: GradingCriteriaRepository):
        self.repository = repository

    def execute(self, command: UpdateGradingCriteriaCommand) -> dict:
        return self.repository.update_grading_criteria(command)
    

class DeleteGradingCriteriaUseCase:
    def __init__(self, repository: GradingCriteriaRepository):
        self.repository = repository

    def execute(self, grading_criteria_id: str) -> None:
        self.repository.delete_grading_criteria(grading_criteria_id)