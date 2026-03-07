from typing import Protocol

from grades.application.dto.grade_dto import CreateGradeCommand, UpdateGradeCommand


class GradeRepository(Protocol):
    def list_grades(self, class_room_id: str | None = None) -> list[dict]:
        ...

    def get_grade(self, grade_id: int) -> dict | None:
        ...

    def create_grade(self, command: CreateGradeCommand) -> dict:
        ...

    def update_grade(self, command: UpdateGradeCommand) -> dict:
        ...

    def delete_grade(self, grade_id: int) -> None:
        ...
