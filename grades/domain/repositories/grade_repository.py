from typing import Protocol

from grades.application.dto.grade_dto import CreateGradeCommand


class GradeRepository(Protocol):
    def list_grades(self, class_room_id: str | None = None) -> list[dict]:
        ...

    def get_grade(self, grade_id: int) -> dict | None:
        ...

    def create_grade(self, command: CreateGradeCommand) -> dict:
        ...
