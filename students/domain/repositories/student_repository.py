from typing import Protocol

from students.application.dto.student_dto import CreateStudentCommand, UpdateStudentCommand


class StudentRepository(Protocol):
    def list_students_detail(self) -> list[dict]:
        ...
    def list_students_by_group(self, group_id: str) -> list[dict]:
        ...

    def list_students_by_classroom(self, classroom_id: str) -> list[dict]:
        ...
    
    def get_student_detail(
        self,
        student_id: str,
        classroom_ids: list[str] | None = None,
    ) -> dict | None:
        ...

    def create_student_with_enrollment(self, command: CreateStudentCommand) -> dict:
        ...

    def update_student(self, command: UpdateStudentCommand) -> dict:
        ...

    def delete_student(self, student_id: str) -> None:
        ...

    def get_student_profile(
        self,
        student_id: str,
        classroom_ids: list[str] | None = None,
    ) -> dict | None:
        ...
