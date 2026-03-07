from typing import Protocol

from academics.application.dto.academics_dto import (
    UpdateClassRoomCommand,
    UpdateEnrollmentCommand,
    UpdateGroupCommand,
    UpdateSubjectCommand,
)


class GroupRepository(Protocol):
    def list_groups(self) -> list[dict]:
        ...

    def get_group(self, group_id: str) -> dict | None:
        ...

    def update_group(self, command: UpdateGroupCommand) -> dict:
        ...


class SubjectRepository(Protocol):
    def list_subjects(self) -> list[dict]:
        ...

    def get_subject(self, subject_id: str) -> dict | None:
        ...

    def update_subject(self, command: UpdateSubjectCommand) -> dict:
        ...


class ClassRoomRepository(Protocol):
    def list_classrooms(self) -> list[dict]:
        ...

    def get_classroom(self, classroom_id: str) -> dict | None:
        ...

    def update_classroom(self, command: UpdateClassRoomCommand) -> dict:
        ...

    def delete_classroom(self, classroom_id: str) -> None:
        ...


class EnrollmentRepository(Protocol):
    def list_enrollments(self) -> list[dict]:
        ...

    def get_enrollment(self, enrollment_id: str) -> dict | None:
        ...

    def update_enrollment(self, command: UpdateEnrollmentCommand) -> dict:
        ...
