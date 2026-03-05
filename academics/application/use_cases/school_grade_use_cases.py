from academics.application.dto.school_grade_dto import CreateSchoolGradeCommand
from academics.domain.entities.school_grade_entity import SchoolGradeEntity
from academics.domain.exceptions.school_grade_exceptions import SchoolGradeNotFoundError
from academics.domain.repositories.school_grade_repository import SchoolGradeRepository


class ListSchoolGradesUseCase:
    def __init__(self, repository: SchoolGradeRepository):
        self.repository = repository

    def execute(self) -> list[dict]:
        return self.repository.list_school_grades()


class GetSchoolGradeUseCase:
    def __init__(self, repository: SchoolGradeRepository):
        self.repository = repository

    def execute(self, school_grade_id: str) -> dict:
        school_grade = self.repository.get_school_grade(school_grade_id)
        if school_grade is None:
            raise SchoolGradeNotFoundError("School Grade not found")
        return school_grade


class CreateSchoolGradeUseCase:
    def __init__(self, repository: SchoolGradeRepository):
        self.repository = repository

    def execute(self, command: CreateSchoolGradeCommand) -> dict:
        SchoolGradeEntity(name=command.name)
        return self.repository.create_school_grade(command)
