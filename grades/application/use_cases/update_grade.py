from grades.application.dto.grade_dto import UpdateGradeCommand
from grades.domain.repositories.grade_repository import GradeRepository


class UpdateGradeUseCase:
    def __init__(self, repository: GradeRepository):
        self.repository = repository

    def execute(self, command: UpdateGradeCommand) -> dict:
        return self.repository.update_grade(command)
