from academics.application.dto.school_grade_dto import UpdateSchoolGradeCommand
from academics.domain.repositories.school_grade_repository import SchoolGradeRepository


class UpdateSchoolGradeUseCase:
    def __init__(self, repository: SchoolGradeRepository):
        self.repository = repository

    def execute(self, command: UpdateSchoolGradeCommand) -> dict:
        return self.repository.update_school_grade(command)
