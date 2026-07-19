from staff.application.dto.staff_dto import CreateStaffCommand, UpdateStaffCommand
from staff.domain.entities.staff_entity import StaffEntity
from staff.domain.repositories.staff_repository import StaffRepository


class ListStaffUseCase:
    def __init__(self, repository: StaffRepository):
        self.repository = repository

    def execute(self) -> list[dict]:
        return self.repository.list_staff()


class CreateStaffUseCase:
    def __init__(self, repository: StaffRepository):
        self.repository = repository

    def execute(self, command: CreateStaffCommand) -> dict:
        first_name = command.first_name.strip()
        last_name = command.last_name.strip()
        username = (command.username or f"{first_name.lower()}_{last_name.lower()}").strip()
        StaffEntity(
            first_name=first_name,
            last_name=last_name,
            username=username,
        )
        if not command.password:
            raise ValueError("password is required")
        if command.role not in {"Admin", "Principal", "Teacher"}:
            raise ValueError("invalid role")
        return self.repository.create_staff(command)


class UpdateStaffUseCase:
    def __init__(self, repository: StaffRepository):
        self.repository = repository

    def execute(self, command: UpdateStaffCommand) -> dict:
        return self.repository.update_staff(command)


class DeleteStaffUseCase:
    def __init__(self, repository: StaffRepository):
        self.repository = repository

    def execute(self, staff_id: str) -> None:
        self.repository.delete_staff(staff_id)
