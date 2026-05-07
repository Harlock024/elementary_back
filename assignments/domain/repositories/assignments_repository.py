from typing import Protocol

from assignments.application.dtos.assignments_dto import CreateAssignmentCommand, UpdateAssignmentCommand


class AttendanceRepository(Protocol):
    def list_assignments(
        self,
        class_id: str | None = None,
        student_id: str | None = None,
    ) -> list[dict]:
        ...

    def create_assignment(self, command: CreateAssignmentCommand) -> dict:
        ...

    def update_assignment(self, command: UpdateAssignmentCommand) -> dict:
        ...

    def delete_assignment(self, assignment_id: str) -> None:
        ...