from grades.application.dto.grade_dto import CreateGradeCommand, UpdateGradeCommand
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
            assignment_id=command.assignment_id,
            subject_id=command.subject_id,
            score=command.score,
        )
        return self.repository.create_grade(command)


class UpdateGradeUseCase:
    def __init__(self, repository: GradeRepository):
        self.repository = repository

    def execute(self, command: UpdateGradeCommand) -> dict:
        return self.repository.update_grade(command)


class DeleteGradeUseCase:
    def __init__(self, repository: GradeRepository):
        self.repository = repository

    def execute(self, grade_id: int) -> None:
        self.repository.delete_grade(grade_id)
