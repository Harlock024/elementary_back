from typing import Protocol

from academics.application.dto.school_grade_dto import CreateSchoolGradeCommand


class SchoolGradeRepository(Protocol):
    def list_school_grades(self) -> list[dict]:
        ...

    def get_school_grade(self, school_grade_id: str) -> dict | None:
        ...

    def create_school_grade(self, command: CreateSchoolGradeCommand) -> dict:
        ...
