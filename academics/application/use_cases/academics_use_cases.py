from academics.application.dto.academics_dto import (
    UpdateClassRoomCommand,
    UpdateEnrollmentCommand,
    UpdateGroupCommand,
    UpdateSubjectCommand,
)
from academics.domain.repositories.academics_repository import (
    ClassRoomRepository,
    EnrollmentRepository,
    GroupRepository,
    SubjectRepository,
)


class UpdateGroupUseCase:
    def __init__(self, repository: GroupRepository):
        self.repository = repository

    def execute(self, command: UpdateGroupCommand) -> dict:
        return self.repository.update_group(command)


class UpdateSubjectUseCase:
    def __init__(self, repository: SubjectRepository):
        self.repository = repository

    def execute(self, command: UpdateSubjectCommand) -> dict:
        return self.repository.update_subject(command)


class UpdateClassRoomUseCase:
    def __init__(self, repository: ClassRoomRepository):
        self.repository = repository

    def execute(self, command: UpdateClassRoomCommand) -> dict:
        return self.repository.update_classroom(command)


class DeleteClassRoomUseCase:
    def __init__(self, repository: ClassRoomRepository):
        self.repository = repository

    def execute(self, classroom_id: str) -> None:
        self.repository.delete_classroom(classroom_id)


class UpdateEnrollmentUseCase:
    def __init__(self, repository: EnrollmentRepository):
        self.repository = repository

    def execute(self, command: UpdateEnrollmentCommand) -> dict:
        return self.repository.update_enrollment(command)
