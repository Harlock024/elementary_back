from typing import Protocol

from students.application.dto.student_dto import CreateStudentCommand


class StudentRepository(Protocol):
    def list_students_detail(self) -> list[dict]:
        ...

    def get_student_detail(self, student_id: str) -> dict | None:
        ...

    def create_student_with_enrollment(self, command: CreateStudentCommand) -> dict:
        ...
