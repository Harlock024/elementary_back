from staff.application.dto.staff_dto import CreateStaffCommand
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
        username = f"{command.first_name.lower()}_{command.last_name.lower()}"
        StaffEntity(
            first_name=command.first_name,
            last_name=command.last_name,
            username=username,
        )
        return self.repository.create_staff(command)
