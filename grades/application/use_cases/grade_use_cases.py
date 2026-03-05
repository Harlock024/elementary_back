from grades.application.dto.grade_dto import CreateGradeCommand
from grades.domain.entities.grade_entity import GradeEntity
from grades.domain.exceptions.grade_exceptions import GradeNotFoundError
from grades.domain.repositories.grade_repository import GradeRepository


class ListGradesUseCase:
    def __init__(self, repository: GradeRepository):
        self.repository = repository

    def execute(self, class_room_id: str | None = None) -> list[dict]:
        return self.repository.list_grades(class_room_id=class_room_id)


class GetGradeUseCase:
    def __init__(self, repository: GradeRepository):
        self.repository = repository

    def execute(self, grade_id: int) -> dict:
        grade = self.repository.get_grade(grade_id)
        if grade is None:
            raise GradeNotFoundError("Grade not found")
        return grade


class CreateGradeUseCase:
    def __init__(self, repository: GradeRepository):
        self.repository = repository

    def execute(self, command: CreateGradeCommand) -> dict:
        GradeEntity(
            student_id=command.student_id,
            class_room_id=command.class_room_id,
            type_code_id=command.type_code_id,
            subject_id=command.subject_id,
            score=command.score,
            max_score=command.max_score,
        )
        return self.repository.create_grade(command)
